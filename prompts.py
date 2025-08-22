from typing import Dict, List, Optional

# Reference content per page. Paste your existing website copy in the strings below.
# Keep content concise; the model will match tone/voice to this reference.
REFERENCE_CONTENT: Dict[str, str] = {
    "OVER_ONS": """Wie zijn wij?
Conduction is een idealistisch IT-bedrijf dat helpt bij het tot stand brengen van goede ideeën en mooie initiatieven. Wij zetten ons in om de digitale wereld te verbeteren, waarbij mens en community altijd centraal staan. Hierom rust onze techniek op de volgende vier pijlers: 
Samen
Wij geloven in de kracht van samen organiseren, daarom ontwikkelen wij het liefst samen. Om zo een idee, droom of ideaal op de beste manier vorm te kunnen geven.
Duurzaam en Innovatief
Alles wat wij maken sluit aan op de behoefte van nu, maar is voorbereid op de toekomst, dat wil zeggen: flexibel genoeg om mee te gaan op bewegingen (on- en offline) van de toekomst.
Open
Alles wat wij ontwikkelen is open source, voor iedereen te gebruiken. Wij geven (onze techniek) graag terug aan de community, zodat anderen er ook mee aan de slag kunnen en mooie concepten kunnen ontwikkelen.
Verantwoord
Op een bewuste en verantwoorde wijze ontwikkelen en ondernemen staat bij ons hoog in het vaandel. Transparantie en eerlijkheid zijn daarbij key, dus daar houden wij ons aan 🙂
Meet the team
Ruben OMDENKER EN HET BREIN ACHTER DE TECHNIEK Ruben is een omdenker en een bouwer. Hij weet de angel van een probleem om te buigen naar een oplossing voor hetzelfde probleem. Daarbij is hij een echte bouwer, of dat nou gaat over code of een community, hij is van vele markten thuis.
Marleen CREATIEF. VERBINDEND EN HOUDT IEDEREEN SCHERP. Marleen is onderzoekend. Met een kleine dosis technical skills, een onuitputtelijke nieuwsgierigheid en een creatieve insteek, onderzoekt zij een vraagstuk/de markt. Om zo alle mogelijkheden te kunnen benutten die tot (online) groei en verbinding kunnen leiden.
Matthias BEWAKER VAN DE KWALITEIT EN COMMERCIEEL. Matthias kenmerkt zich door zijn sterke interesse in techniek, zijn pragmatische instelling, zijn hoge doorzettingsvermogen en zijn goede communicatieve vaardigheden. Matthias komt met ongewone oplossingen voor hardnekkige problemen.
Robert OBSERVANT. DEVELOPER MET SCHERPE ZINTUIGEN Robert is een toegewijde developer en er ontgaat hem niks. Puzzelen met code en tot een gerichte oplossing komen, daar wordt hij heel blij van.
Wilco TEAMPLAYER Wilco houdt van programmeren, oplossingen bedenken en van mensen (verder) helpen. Hij combineert die twee dingen binnen het team als vanzelf.
Barry AANPAKKER. DEVELOPER DIE VAN AANPAKKEN WEET. Barry is nieuwsgierig en open. Hij heeft een enorme drive. He gets things done!""",
    "BEHEER": """Beheer
Product:
Uw gemeente wil graag aan de slag met Common Ground, of wil een Common Ground applicatie gebruiken. Maar u heeft nog geen ervaring met kubernetes en of het draaien van Common Ground applicaties? Geen probleem, we ontzorgen u van A tot Z en verzorgen zowel het beheer van uw omgevingen, certificaten als het installeren en onderhouden van componenten en applicaties. Zo bent u snel online zonder de zorgen. Wilt u later de omgeving in eigen beheer? Geen probleem, wij dragen de omgeving graag aan u over.
Wil je weten of de Nextcloud iets voor jouw gemeente is?
Beheer goed geregeld
Uw eigen private cloud
Om uw Common Ground applicaties en componenten te installeren richten wij voor u een eigen private cloud in volgens het Haven principe. Hierbij ontzorgen wij met de implementatie, ondersteuning en onderhoud, zodat u zekerheid heeft van een supportovereenkomst voor het beheer van uw omgeving.
Aangepast op uw behoefte
De eisen tot de infrastructuur voor uw omgeving worden in grote mate bepaald door het aantal componenten en de intensiteit van het gebruik. Dit betekent dat u zelfs kunt bepalen of uw cloud inhouse of extern draait.
Nextcloud
Nextcloud, het Europese open source alternatief voor Microsoft 365. Wij leveren een Nextcloud-omgeving op maat, die voldoet aan Common Ground-principes en volledig onder eigen regie draait. U kiest zelf of u deze omgeving lokaal, in de cloud of in een datacenter laat hosten — zonder vendor lock-in.
Eén aanspreekpunt
Met onze beheer propositie biedt Conduction één aanspreekpunt voor software, installatie en beheer. Hierdoor heeft u één aanspreekpunt voor support voor alles. Er is geen onduidelijkheid over bij wie de verantwoordelijkheid ligt als er issues optreden. Alles valt binnen één Service Level Agreement.
Applicaties
Alle Common Ground applicaties kunnen in beheer worden gebracht op Nextcloud zolang ze voldoen aan de standaarden. Ook niet- Common Ground applicaties kunnen op Nextcloud draaien. Deze worden met maatwerk passend gemaakt.
DashKube
DashKube is een Kubernetes georiënteerd dashboard dat organisaties en ontwikkelaars helpt om eenvoudig een Kubernetes-omgeving op te zetten en te configureren. Door de Kubernetes-management tool is het niet meer nodig Kubernetes te leren en is je ecosysteem binnen no time up and running. Voor meer informatie bezoek DashKube.""",
    "PROJECTEN": """Projecten
In de afgelopen jaren heeft Conduction samen met verschillende overheidsinstanties en leveranciers gewerkt aan projecten, waarbij volgens de Common Ground principes applicaties en componenten zijn ontwikkeld.
Hieronder worden die projecten weergegeven. 
Nieuwsgierig naar wat Conduction voor jou kan betekenen?
OpenWoo.app
OpenWoo.app helpt gemeenten om documenten rechtstreeks vanuit hun bronsystemen te ontsluiten en automatisch te publiceren — zónder dat daar een aparte Woo-taakapplicatie voor nodig is.
Met deze oplossing krijgen inwoners, journalisten en onderzoekers beter toegang tot overheidsinformatie. Zo voldoet de gemeente niet alleen aan de eisen van de Woo, maar sluit ze ook beter aan bij de informatiebehoefte van de samenleving.
OpenWoo.app is gebouwd op de Common Ground-principes en daarmee flexibel in gebruik: gemeenten kiezen zelf welke frontendpartij de data ontsluit. De oplossing is gebaseerd op Nextcloud en volledig open source beschikbaar
OpenCatalogi
OpenCatalogi helpt overheden om grip te krijgen op hun applicatielandschap. Informatie over applicaties, leveranciers, standaarden en API’s wordt overzichtelijk vastgelegd en gedeeld via een federatief model.
Elke organisatie behoudt de regie over de eigen gegevens, terwijl er toch een gedeeld, actueel overzicht ontstaat voor de hele publieke sector.
De dienst is modulair opgezet en draait op een infrastructuur die we delen met andere projecten, waaronder OpenWoo.app en OpenRegisters. Die gezamenlijke basis — gebaseerd op open source componenten waaronder Nextcloud — zorgt voor betrouwbaarheid, schaalbaarheid en koppelbaarheid tussen oplossingen.
OpenCatalogi is ontwikkeld vanuit de Common Ground-gedachte en groeit continu door actieve samenwerking met gemeenten en leveranciers.
VNG Softwarecatalogus
De VNG Softwarecatalogus helpt gemeenten bij het beheren en inzichtelijk maken van hun applicatielandschap. Gemeenten registreren hier welke software ze gebruiken, hoe deze is gekoppeld, welke oplossingen beschikbaar zijn en welke standaarden worden toegepast.
Zo ontstaat er een gedeeld overzicht dat samenwerking, inkoop en interoperabiliteit binnen het gemeentelijk domein versterkt.
De vernieuwing van de Softwarecatalogus wordt ontwikkeld in opdracht van VNG Realisatie en is gebaseerd op OpenCatalogi. Onderliggend maakt het gebruik van dezelfde modulaire componenten als OpenWoo.app. Dit zorgt voor een samenhangende en herbruikbare infrastructuur, volledig open source.
OpenRegisters
OpenRegisters is een krachtige open source-oplossing voor het opslaan, beheren en ontsluiten van gegevens. Gemeenten gebruiken het bijvoorbeeld om een verwerkingenregister of publicatieomgeving op te bouwen — maar de toepassing is veel breder: elk type register of gegevensverzameling kan ermee worden ingericht.
Van een gemeentelijk verwerkingsregister tot de ledenadministratie van een sportvereniging: OpenRegisters biedt de flexibiliteit om je eigen structuur en datamodellen samen te stellen.
Het platform draait bovenop Nextcloud en wordt gezien als een open source alternatief voor Microsoft Access — maar dan flexibeler, webgebaseerd en volledig koppelbaar met andere toepassingen.
OpenRegisters vormt ook de basis onder andere producten zoals OpenWoo.app, OpenCatalogi en de VNG Softwarecatalogus, en is gebouwd op een modulaire infrastructuur die hergebruik en integratie eenvoudig maakt.
Waardepapieren
Waardepapieren is een dienst waarbij burgers uittreksels digitaal kunnen opvragen bij de gemeente. Voorheen was de burger altijd genoodzaakt om diverse waardepapieren af te halen bij de gemeente, dat kan nu online!
Met waardepapieren is het mogelijk om BRP of woonhistorie uittreksels digitaal aan te vragen en deze vervolgens zelf uit te printen.""",
    "COMMON_GROUND": """Common Ground
Gemeenten hebben een nieuwe, moderne, gezamenlijke informatievoorziening nodig voor het uitwisselen van gegevens. Want het huidige stelsel voor gegevensuitwisseling maakt het lastig om snel en flexibel te vernieuwen, te voldoen aan privacywetgeving en efficiënt om te gaan met data. Dat staat de verbetering van de gemeentelijke dienstverlening in de weg. Dus tijd voor een nieuwe beweging: Common Ground werd geboren, waarbij hervorming van de huidige gemeentelijke informatievoorziening, deelbaarheid, data bij de bron en vooral de burger centraal staat.
Meer weten wat Conduction voor jouw gemeente kan betekenen?
Conduction <3 Common Ground
Wij geloven in online gemeenschappen en samen organiseren. Wij geloven in delen, duurzaamheid en transparantie. Vanuit deze gedachte zijn we ook toegetreden tot het Common Ground initiatief van de Nederlandse Gemeenten. Binnen dit initiatief staat samenwerking en publiek eigenaarschap centraal. Sinds 3 Juli 2019 zijn wij ook toegetreden tot het groeipact Common Ground. Met het ondertekenen van dit convenant proberen wij een actieve bijdrage te leveren aan het succes van Common Ground. Dit doen wij door onze techniek volgens de Common Ground principes te ontwikkelen.
Onze successen
In de afgelopen jaren heeft Conduction, als ontwikkelpartij, in partnerschap met overheidsorganisaties meegewerkt aan verschillende innovatieprojecten. De applicaties zijn ontwikkeld volgens de Common Ground principes en open source beschikbaar en deelbaar. Benieuwd naar onze projecten?
Advisering
De expertise die Conduction heeft bieden wij ook aan in de vorm van documentatie, tutorials of adviesgesprekken. Onze gespecialiseerde vaardigheden binnen de IT delen wij graag om tot oplossingen te komen. Een afspraak voor een vrijblijvend gesprek is altijd mogelijk.
Trainingen
Conduction heeft veel ervaring opgedaan rondom Common Ground ontwikkeling, beheer van omgevingen en software. Wij hebben daarom trainingen ontwikkeld op deze gebieden. De trainingen zijn niet alleen voor gemeenten en overheden, maar ook voor Common Ground minded leveranciers.
Development
Conduction ontwikkelt open source software op basis van Common Ground en moderne standaarden.
Van maatwerk tot modulaire componenten: we bouwen oplossingen die passen bij de behoeften van gemeenten en publieke organisaties.
Onze ervaring zetten we graag in voor jouw project of productidee.""",
    "TRAININGEN": """Trainingen
Conduction heeft veel ervaring opgedaan rondom Common Ground ontwikkeling, beheer van omgevingen en software. Wij hebben daarom trainingen ontwikkeld op deze gebieden. De trainingen zijn niet alleen voor gemeenten en overheden, maar ook voor Common Ground minded leveranciers.
Meer weten over onze trainingen. Neem contact op
Alle trainingen
Basis Common Ground - Voor iedereen die wil starten met Common Ground. Een korte introductie in Common Ground. Waar we inzoomen op de principes, voordelen, uitdagingen en lopende projecten.
Architectuur Common Ground - Voor architecten, informatiemanagers en product owners. Met deze training kijken we naar de architectuurprincipes van Common ground en passen we die hands-on toe.
API Ontwerpen - Voor developers en architecten. Een technische training waarin we de “good practices” van API ontwikkeling volgens Common Ground behandelen.
Open Source Software Development - Voor developers en product owners. Wanneer je open source software wilt ontwikkelen loop je tegen unieke uitdagingen aan. Deze training helpt je de uitdagingen het hoofd te bieden.
Privacy by Design - Voor iedereen. Privacy by design is een denkwijze waarmee je de “privacy arm” systemen kan ontwikkelen. Dit zorgt voor een lagere AVG impact.
Haven/ Kubernetes - Voor beheerders. Bij deze training kijken we naar laag 0 van het Common Ground model. We duiken in Kubernetes en wat de Haven standaard is en wat het niet is.""",
    "LINKEDIN": """[0] ✨ Trots moment bij Conduction! ✨
We zijn verheugd te kunnen delen dat Conduction opnieuw met succes de ISO 27001 én ISO 9001 certificeringen heeft behaald! 🎉
Deze certificeringen bevestigen dat wij voldoen aan de hoogste normen op het gebied van informatiebeveiliging (ISO 27001) en kwaliteitsmanagement (ISO 9001). Het laat zien dat we niet alleen veilige en betrouwbare oplossingen bouwen, maar ook continu werken aan procesverbetering en klanttevredenheid.
Een groot dankjewel aan ons team voor hun toewijding én aan Brand Compliance B.V. voor het afnemen van de audits! 🙌
Meer over ons kwaliteitsbeleid lees je hier:
[1]Genomineerd voor de Computable Awards 2025!
Het innovatieproject ‘Anonimiseren met LLM’, waarin Gemeente Hoeksche Waard de krachten bundelt met de Gemeente Barendrecht, Gemeente Ridderkerk, Gemeente Alblasserdam, Gemeente Buren en Gemeente Krimpen aan den IJssel, is genomineerd voor de Computable Awards 2025 in de categorie Overheidsproject.
Met dit project ontwikkelen we een digitale oplossing die automatisch persoonsgegevens –zoals namen, adressen en BSN’s – in teksten herkent en anonimiseert met behulp van slimme taalmodellen (LLM’s). Zo kunnen documenten gedeeld worden zonder dat de privacy van burgers wordt aangetast.
De oplossing wordt open source ontwikkeld binnen het Open Webconcept, zodat ook andere overheden deze technologie kunnen hergebruiken of verder ontwikkelen. De technische uitvoering ligt bij Conduction en het project wordt mede mogelijk gemaakt met innovatiebudgetten van Rijksorganisatie voor Ontwikkeling, Digitalisering en Innovatie (Ministerie van BZK).
Stem kan tot en met 13 oktober: https://lnkd.in/eYTNpvG
Onder de categorie: Overheidsproject ->  Anonimiseren met LLM (Gemeente Hoeksche Waard)
#OpenSource hashtag#CommonGround hashtag#AI hashtag#Privacy hashtag#Digitalisering hashtag#OpenWebconcept hashtag#ComputableAwards
[2] 📣 Reflectie op hashtag#NextcloudSummit2025: wat kan Nederland leren van Europa op het gebied van datasoevereiniteit?
Tijdens zijn terugreis uit München zette onze collega zijn gedachten op een rij over hoe Europa – en Nederland – in hoog tempo loskomt van big tech. 🇪🇺
 📌 Frankrijk en Duitsland lopen voorop
 📌 Nederland komt op gang, maar laat kansen liggen
 📌 Europa biedt een tenderloze route naar open source
 📌 Eurostack en Common Ground: andere fundamenten, zelfde missie
 📌 AI dwingt tot herbezinning op data-opslag en applicatiearchitectuur
 📌 En: waar ligt nu eigenlijk écht de grootste bedreiging?
👉 Een must-read over IT-beleid, open source, AI en datastrategie voor de publieke sector:
🔗 Lees het hele stuk hier: https://lnkd.in/ei53BXQn
#OpenSource hashtag#CommonGround hashtag#DigitalSovereignty hashtag#PublicSector hashtag#Nextcloud hashtag#AI hashtag#Overheid hashtag#EU""",
    # Fallback voor algemene website-secties wanneer geen keyword is herkend
    "HOME": """Public Tech
Wij zijn wat je zou kunnen noemen Digital Socials, wij ontwikkelen techniek volgens de Common Ground principes, waarbij mens en community centraal staan. Graag dragen we dan ook bij aan het ontwikkelen van digitale oplossingen voor maatschappelijke vraagstukken:
‘Tech to serve people’.
Meer weten over ons bedrijf? Plan een afspraak.
Wat wij doen
Beheer - Conduction beschikt over een brede kennis van Kubernetes en Haven. Wij helpen met het faciliteren en beheren van omgevingen en bieden ook ondersteuning bij implementaties. Lees meer.
Common Ground - Conduction levert een actieve bijdrage aan het succes van Common Ground. Dit doen we door al onze techniek volgens de Common Ground principes te ontwikkelen. Wij adviseren overheden en leveranciers hoe zij succesvol kunnen zijn binnen Common Ground. Lees meer.
Ontwikkelen - Conduction ontwikkelt open source software voor overheden en leveranciers. Als idealistische partij zetten wij ons in voor innovatie van diensten en hebben wij aan meerdere innovatieprojecten meegewerkt. Lees meer.
Trainingen - Conduction heeft veel ervaring opgedaan rondom Common Ground ontwikkeling, beheer van omgevingen en software. Deze ervaring delen wij graag met u in de vorm van trainingen en adviezen. Benieuwd hoe wij u kunnen helpen? Lees meer.""",
}


def build_system_prompt(page_key: str) -> str:
    """
    Return a system prompt tailored to a specific page, including reference content.

    @param page_key: Canonical page identifier (e.g., 'OVER_ONS', 'LINKEDIN').
    @returns: Prompt string for the language model.
    """
    reference = REFERENCE_CONTENT.get(page_key, REFERENCE_CONTENT["HOME"]) or ""
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
        "Geef de output in Markdown.\n\n"
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

