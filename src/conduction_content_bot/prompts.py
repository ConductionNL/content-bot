from typing import Dict, List, Optional
from .content_fetcher import get_reference_content
import os
import json
import logging


# Reference content per page is stored in an external JSON file.
def _load_reference_content() -> Dict[str, str]:
    try:
        json_path = os.path.join(os.path.dirname(__file__), "reference_content.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
    except Exception as e:
        logging.exception(f"Error loading reference content: {e}")
        pass
    return {}


REFERENCE_CONTENT: Dict[str, str] = _load_reference_content()


def build_system_prompt(page_key: str) -> Optional[str]:
    """
    Return a system prompt tailored to a specific page, including reference content.

    @param page_key: Canonical page identifier (e.g., 'OVER_ONS', 'LINKEDIN').
    @returns: Prompt string for the language model.
    """
    # Prefer live-site content; fallback to local reference strings
    try:
        live_reference = get_reference_content(page_key)
    except Exception as e:
        logging.exception(f"Error fetching reference content: {e}")
        return None

    reference = (
        live_reference
        or REFERENCE_CONTENT.get(page_key)
        or REFERENCE_CONTENT.get("HOME", "")
    )
    if page_key == "LINKEDIN":
        return (
            "Schrijf een korte LinkedIn-post in het Nederlands, menselijk en to-the-point. "
            "Vermijd buzzwords, eindig met een natuurlijke call-to-action of vraag. "
            "Match de tone-of-voice met de referenties hieronder.\n\n"
            f"Referentie (LinkedIn):\n{reference}"
        )
    # Unified prompt for all website pagina's (niet-LinkedIn)
    return (
        "Schrijf een compacte paragraaf (Markdown) die past bij de gekozen website-pagina. "
        "Schrijf aanvullend op de bestaande inhoud: voeg nieuwe, relevante informatie toe die logisch in de huidige context past. "
        "Vermijd herhaling van informatie die al op de pagina staat. "
        "Tone-of-voice: helder, nuchter, professioneel maar menselijk. "
        "Geef de output in Markdown. LET OP: de voorbeeldtekst is in html maar de output moet in markdown zijn.\n\n"
        f"Referentie:\n{reference}"
    )


# Map van herkenbare keywords naar page keys.
# Voeg hier varianten/synoniemen toe als dat handig is.
KEYWORD_TO_PAGE: Dict[str, str] = {
    "over ons": "OVER_ONS",
    "overons": "OVER_ONS",
    "beheer": "BEHEER",
    "managed": "BEHEER",
    "projecten": "PROJECTEN",
    "project": "PROJECTEN",
    "common ground": "COMMON_GROUND",
    "commonground": "COMMON_GROUND",
    "trainingen": "TRAININGEN",
    "training": "TRAININGEN",
    "linkedin": "LINKEDIN",
    "linkedin post": "LINKEDIN",
    "post": "LINKEDIN",
    "home": "HOME",
}


# Representative, "mooiste" display-key per unieke page key.
# De volgorde hieronder bepaalt de weergavevolgorde in help/reset-berichten.
PAGE_TO_DISPLAY_KEY: Dict[str, str] = {
    "OVER_ONS": "over ons",
    "BEHEER": "beheer",
    "PROJECTEN": "projecten",
    "COMMON_GROUND": "common ground",
    "TRAININGEN": "trainingen",
    "LINKEDIN": "linkedin",
    "HOME": "home",
}


def detect_page_key(user_text: str) -> Optional[str]:
    """
    Detect the canonical page key from user-provided text.

    @param user_text: Raw user text possibly containing a known keyword.
    @returns: Matching page key or None if not found.
    """
    text = (user_text or "").strip().lower()
    if not text:
        return None
    # Zoek naar de langste match (zodat 'linkedin post' boven 'linkedin' gaat)
    candidates: List[str] = sorted(KEYWORD_TO_PAGE.keys(), key=lambda k: -len(k))
    for keyword in candidates:
        if keyword in text:
            return KEYWORD_TO_PAGE[keyword]
    return None
