"""Utilities to fetch website content and extract readable HTML snippets.

This module provides a tiny in-memory cache and HTML extraction using
`trafilatura` and `BeautifulSoup` to return simplified HTML suitable for
downstream consumption.
"""

import os
import time
from typing import Dict, Optional, Tuple
from urllib import request
from urllib.parse import urljoin
from urllib.error import HTTPError, URLError
import trafilatura
from bs4 import BeautifulSoup

WEBSITE_BASE_URL = os.getenv("WEBSITE_BASE_URL", "https://conduction.nl")

PAGE_TO_URL: Dict[str, str] = {
    # Replace with your real URLs or paths
    "OVER_ONS": "/over-ons",
    "BEHEER": "/beheer",
    "PROJECTEN": "/projecten",
    "COMMON_GROUND": "/common-ground",
    "TRAININGEN": "/trainingen",
    "HOME": "/",
}

_CACHE: Dict[str, Tuple[float, str]] = {}
_TTL_SECONDS: float = 3600.0

def get_reference_content(page_key: str) -> str:
    """Return readable HTML content for a configured page key.

    @param page_key: Key in ``PAGE_TO_URL`` identifying which page to fetch.
    @return: Extracted HTML string, or empty string on failure.
    @rtype: str
    """
    result = fetch_page_html(page_key)
    return result if result else ""

def fetch_page_html(page_key: str) -> Optional[Tuple[str, str]]:
    """Fetch a page by key, with simple in-memory caching and extraction.

    If cached and non-empty, returns a tuple of ``(url, cached_html)``.
    If fetched fresh, returns the extracted HTML string. Returns ``None``
    on failure to resolve or fetch.

    @param page_key: Key in ``PAGE_TO_URL`` identifying which page to fetch.
    @return: Either ``(url, html)`` when served from cache, the HTML string
        when fetched fresh, or ``None`` on failure.
    @rtype: Optional[Tuple[str, str]] or str
    """
    url = _resolve_url(page_key)
    if not url:
        return None
    now = time.time()
    cache_key = f"live:{url}"
    cached = _CACHE.get(cache_key)
    if cached and (now - cached[0]) < _TTL_SECONDS:
        cached_text = cached[1] or ""
        if cached_text.strip():
            return url, cached_text
        # Invalidate empty cache entry and refetch
        try:
            del _CACHE[cache_key]
        except Exception:
            pass
    html_str = _http_get(url)
    if html_str is None:
        return None
    text = _extract_text_from_html(html_str)
    return text

def _resolve_url(page_key: str) -> Optional[str]:
    """Resolve a page key to an absolute URL.

    @param page_key: Key in the ``PAGE_TO_URL`` mapping.
    @return: Absolute URL if known; otherwise ``None``.
    @rtype: Optional[str]
    """
    target = PAGE_TO_URL.get(page_key)
    if not target:
        return None
    if target.startswith("http://") or target.startswith("https://"):
        return target
    return urljoin(WEBSITE_BASE_URL.rstrip("/") + "/", target.lstrip("/"))

def _http_get(url: str) -> Optional[str]:
    """Perform a simple HTTP GET using a custom User-Agent.

    @param url: Absolute URL to request.
    @return: Response body decoded as UTF-8, or ``None`` on error.
    @rtype: Optional[str]
    """
    try:
        req = request.Request(url, headers={"User-Agent": "conduction-content-bot"})
        with request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None


def _extract_text_from_html(html_str: str) -> str:
    """Extract readable content from HTML and normalize to basic tags.

    Enriches the extracted HTML with header text (title, paragraphs, primary
    links) from the original page when available, then keeps only basic
    content tags and minimal attributes.

    @param html_str: Raw HTML document string.
    @return: Sanitized, minimal HTML string.
    @rtype: str
    """
    # extract main article HTML
    extracted = trafilatura.extract(
        html_str,
        output_format="html",
        favor_precision=True,
        include_tables=False,
        include_comments=False,
    )
    # If nothing was extracted, continue so we can append the header text from the original HTML.
    if not extracted:
        extracted = ""

    # Build a soup from the extracted content
    soup = BeautifulSoup(extracted, "html.parser")

    # add the header text to the content
    try:
        original = BeautifulSoup(html_str, "html.parser")
        hero = original.select_one("header.hero, .heroBanner_qdFl, .hero")
        if hero:
            header_tag = soup.new_tag("header")

            title_node = hero.find(["h1", "h2", "h3"])
            if title_node and title_node.get_text(strip=True):
                title_tag = soup.new_tag("h1")
                title_tag.string = title_node.get_text(strip=True)
                header_tag.append(title_tag)
            for p_node in hero.find_all("p"):
                text = p_node.get_text(strip=True)
                if text:
                    p_tag = soup.new_tag("p")
                    p_tag.string = text
                    header_tag.append(p_tag)
            for a_node in hero.select(".buttons_AeoN a, a.primaryHeroLink_NsbJ"):
                link_text = a_node.get_text(strip=True)
                if link_text:
                    a_tag = soup.new_tag("a")
                    href_val = a_node.get("href")
                    if href_val:
                        a_tag["href"] = href_val
                    a_tag.string = link_text
                    header_tag.append(a_tag)
            if header_tag.contents:
                # Insert header children directly at the top without the <header> wrapper
                children = list(header_tag.contents)
                for child in children:
                    child.extract()
                for child in reversed(children):
                    soup.insert(0, child)

    except Exception:
        # Best-effort enrichment; ignore failures and fall back to extracted content only
        pass

    # 3) keep just basic content tags
    allowed = {"header", "p","h1","h2","h3","h4","h5","h6","ul","ol","li","strong","em","a","blockquote","pre","code","br"}
    for tag in list(soup.find_all(True)):
        if tag.name not in allowed:
            tag.unwrap()
        else:
            tag.attrs = {"href": tag.get("href")} if tag.name == "a" and tag.has_attr("href") else {}

    return str(soup)