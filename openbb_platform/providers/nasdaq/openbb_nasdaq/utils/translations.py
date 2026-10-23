"""Nasdaq Nordic Label Translations.

The Danish fixed-income reference tables are published untranslated - the
``lang`` parameter is accepted but ignored - so their labels are mapped here.
"""

DANISH_LABELS = {
    "Rente før skat - restløbetid (år)": (
        "Yield before tax - residual maturity (years)"
    ),
    "Rente efter skat - restløbetid (år)": (
        "Yield after tax - residual maturity (years)"
    ),
    "Alm & Særl. realkredit": "Ordinary & special mortgage credit",
    "Enhedsprioritet": "Unit priority mortgage",
    "Stat, fiskeri & Færøerne": "Government, fisheries & Faroe Islands",
    "Særlige institutter": "Special institutions",
    "Antal papirer": "Number of securities",
    "Effektiv rente": "Effective yield",
    "Vægt i %": "Weight in %",
    "Kreditor indeksfaktorer: Restgæld/obligationer": (
        "Creditor index factors: Outstanding debt/bonds"
    ),
    "Debitor indeksfaktorer: Ejebolig, hovedstol": (
        "Debtor index factors: Owner-occupied housing, principal"
    ),
    "Indekskorrektionsfaktorer: Restgæld/obligationer": (
        "Index correction factors: Outstanding debt/bonds"
    ),
    "Støttet byggeri, hovedstol": "Subsidised construction, principal",
    "Rederiindeks 1 1/2 pct": "Shipping index 1.5 pct",
    "Rederiindeks 3 pct.": "Shipping index 3 pct",
    "Referenceindeks:": "Reference index",
}


def translate(label) -> str | None:
    """Render a Nasdaq Nordic label in English.

    Parameters
    ----------
    label : Any
        The label as published.

    Returns
    -------
    str or None
        The English label, or the original when it needs no translation.
    """
    if label is None:
        return None

    text = str(label).strip().rstrip(":")

    return DANISH_LABELS.get(text, DANISH_LABELS.get(str(label).strip(), text))
