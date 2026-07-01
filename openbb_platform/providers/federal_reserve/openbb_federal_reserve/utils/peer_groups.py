"""FFIEC UBPR peer-group registry.

Resolves a UBPR peer-group ``name`` (e.g. ``"1"``, ``"NATIONAL"``, ``"ALCOM"``)
to the ``peergroupid`` carried in ``UbprReport.aspx`` URLs. The id is an arbitrary
stable internal identifier and is not unique across the ``conceptname`` categories,
so the registry is keyed on the peer-group name.

The live registry is fetched from the report router's ``PGSelector`` request; a
baked snapshot (:data:`STATIC_PEER_GROUPS`) lets the dropdown options be built at
import time without a network call, and serves as the fallback when the live fetch
is unavailable.

``conceptname`` categories
--------------------------
- ``UBPPD186`` size/type peer groups (insured commercial/savings banks, credit-card
  specialty, denovo, bankers banks, trust companies).
- ``UBPPM277`` mutually- and stock-owned savings-bank peer groups.
- ``UBPPF861`` national rollups (``COM``, ``SVG``, ``CRC``, ``BKR``, ``NDT``).
- ``UBPPF863`` per-state peer groups (the State Average report's keys).
- ``UBPPF865`` trust-asset peer groups.
- ``UBPPF866`` the ``NATIONAL`` all-bank rollup.
"""

from __future__ import annotations

from typing import Any

STATIC_PEER_GROUPS: dict[str, tuple[int, str, str]] = {
    "1": (
        4,
        "Insured commercial banks having assets greater than $100 billion",
        "UBPPD186",
    ),
    "101": (
        20,
        "Insured savings banks having assets greater than $1 billion",
        "UBPPD186",
    ),
    "101M": (
        357,
        "Mutually-owned insured savings banks having assets greater than $1 billion",
        "UBPPM277",
    ),
    "101S": (
        358,
        "Stock-owned insured savings banks having assets greater than $1 billion",
        "UBPPM277",
    ),
    "102": (
        21,
        "Insured savings banks having assets between $300 million and $1 billion",
        "UBPPD186",
    ),
    "102M": (
        359,
        "Mutually-owned insured savings banks having assets between $300 million and $1 billion",
        "UBPPM277",
    ),
    "102S": (
        360,
        "Stock-owned insured savings banks having assets between $300 million and $1 billion",
        "UBPPM277",
    ),
    "103": (
        22,
        "Insured savings banks having assets between $100 million and $300 million",
        "UBPPD186",
    ),
    "103M": (
        361,
        "Mutually-owned insured savings banks having assets between $100 million and $300 million",
        "UBPPM277",
    ),
    "103S": (
        362,
        "Stock-owned insured savings banks having assets between $100 million and $300 million",
        "UBPPM277",
    ),
    "104": (
        23,
        "Insured savings banks having assets less than $100 million",
        "UBPPD186",
    ),
    "104M": (
        363,
        "Mutually-owned insured savings banks having assets less than $100 million",
        "UBPPM277",
    ),
    "104S": (
        364,
        "Stock-owned insured savings banks having assets less than $100 million",
        "UBPPM277",
    ),
    "2": (
        5,
        "Insured commercial banks having assets between $10 billion and $100 billion",
        "UBPPD186",
    ),
    "201": (
        25,
        "Credit card specialty banks having assets greater than $ 3 billion",
        "UBPPD186",
    ),
    "202": (
        26,
        "Credit card specialty banks having assets between $1 billion and $3 billion",
        "UBPPD186",
    ),
    "2022": (
        53,
        "Denovo banks opened in 2022 having assets less than $750 million",
        "UBPPD186",
    ),
    "2023": (
        54,
        "Denovo banks opened in 2023 having assets less than $750 million",
        "UBPPD186",
    ),
    "2024": (
        55,
        "Denovo banks opened in 2024 having assets less than $750 million",
        "UBPPD186",
    ),
    "2025": (
        56,
        "Denovo banks opened in 2025 having assets less than $750 million",
        "UBPPD186",
    ),
    "2026": (
        57,
        "Denovo banks opened in 2026 having assets less than $750 million",
        "UBPPD186",
    ),
    "203": (
        27,
        "Credit card specialty banks having assets less than $1 billion",
        "UBPPD186",
    ),
    "3": (
        6,
        "Insured commercial banks having assets between $3 billion and $10 billion",
        "UBPPD186",
    ),
    "301": (28, "Bankers banks", "UBPPD186"),
    "4": (
        7,
        "Insured commercial banks having assets between $1 billion and $3 billion",
        "UBPPD186",
    ),
    "401": (29, "All Non-insured Non-deposit Trust Companies", "UBPPD186"),
    "5": (
        8,
        "Insured commercial banks having assets between $300 million and $1 billion",
        "UBPPD186",
    ),
    "6": (
        9,
        "Insured commercial banks having assets between $100 million and $300 million",
        "UBPPD186",
    ),
    "7": (
        10,
        "Insured commercial banks having assets between $50 million and $100 million",
        "UBPPD186",
    ),
    "8": (
        11,
        "Insured commercial banks having assets less than $50 million",
        "UBPPD186",
    ),
    "AKCOM": (237, "All Insured Commercial Banks in Alaska", "UBPPF863"),
    "AKSVG": (293, "All Insured Savings Banks in Alaska", "UBPPF863"),
    "ALCOM": (236, "All Insured Commercial Banks in Alabama", "UBPPF863"),
    "ALSVG": (292, "All Insured Savings Banks in Alabama", "UBPPF863"),
    "ARCOM": (240, "All Insured Commercial Banks in Arkansas", "UBPPF863"),
    "ARSVG": (296, "All Insured Savings Banks in Arkansas", "UBPPF863"),
    "AZCOM": (239, "All Insured Commercial Banks in Arizona", "UBPPF863"),
    "AZNDT": (71, "All Non-insured Non-deposit Trust Companies in Arizona", "UBPPF863"),
    "AZSVG": (295, "All Insured Savings Banks in Arizona", "UBPPF863"),
    "BKR": (30, "Bankers banks", "UBPPF861"),
    "CABKR": (129, "All Bankers Banks in California", "UBPPF863"),
    "CACOM": (241, "All Insured Commercial Banks in California", "UBPPF863"),
    "CANDT": (
        73,
        "All Non-insured Non-deposit Trust Companies in California",
        "UBPPF863",
    ),
    "CASVG": (297, "All Insured Savings Banks in California", "UBPPF863"),
    "COBKR": (130, "All Bankers Banks in Colorado", "UBPPF863"),
    "COCOM": (242, "All Insured Commercial Banks in Colorado", "UBPPF863"),
    "COM": (3, "All insured commercial banks", "UBPPF861"),
    "COSVG": (298, "All Insured Savings Banks in Colorado", "UBPPF863"),
    "CRC": (24, "All credit card specialty banks", "UBPPF861"),
    "CTCOM": (243, "All Insured Commercial Banks in Connecticut", "UBPPF863"),
    "CTSVG": (299, "All Insured Savings Banks in Connecticut", "UBPPF863"),
    "DCCOM": (245, "All Insured Commercial Banks in District of Columbia", "UBPPF863"),
    "DECOM": (244, "All Insured Commercial Banks in Delaware", "UBPPF863"),
    "DECRC": (188, "All Credit Card Specialty Banks in Delaware", "UBPPF863"),
    "DENDT": (
        76,
        "All Non-insured Non-deposit Trust Companies in Delaware",
        "UBPPF863",
    ),
    "DESVG": (300, "All Insured Savings Banks in Delaware", "UBPPF863"),
    "FLCOM": (246, "All Insured Commercial Banks in Florida", "UBPPF863"),
    "FLCRC": (190, "All Credit Card Specialty Banks in Florida", "UBPPF863"),
    "FLNDT": (78, "All Non-insured Non-deposit Trust Companies in Florida", "UBPPF863"),
    "FLSVG": (302, "All Insured Savings Banks in Florida", "UBPPF863"),
    "FMCOM": (261, "All Insured Commercial Banks in Micronesia", "UBPPF863"),
    "GACOM": (247, "All Insured Commercial Banks in Georgia", "UBPPF863"),
    "GANDT": (79, "All Non-insured Non-deposit Trust Companies in Georgia", "UBPPF863"),
    "GASVG": (303, "All Insured Savings Banks in Georgia", "UBPPF863"),
    "GUCOM": (248, "All Insured Commercial Banks in Guam", "UBPPF863"),
    "HICOM": (249, "All Insured Commercial Banks in Hawaii", "UBPPF863"),
    "IACOM": (253, "All Insured Commercial Banks in Iowa", "UBPPF863"),
    "IANDT": (85, "All Non-insured Non-deposit Trust Companies in Iowa", "UBPPF863"),
    "IASVG": (309, "All Insured Savings Banks in Iowa", "UBPPF863"),
    "IDCOM": (250, "All Insured Commercial Banks in Idaho", "UBPPF863"),
    "IDSVG": (306, "All Insured Savings Banks in Idaho", "UBPPF863"),
    "ILCOM": (251, "All Insured Commercial Banks in Illinois", "UBPPF863"),
    "ILNDT": (
        83,
        "All Non-insured Non-deposit Trust Companies in Illinois",
        "UBPPF863",
    ),
    "ILSVG": (307, "All Insured Savings Banks in Illinois", "UBPPF863"),
    "INCOM": (252, "All Insured Commercial Banks in Indiana", "UBPPF863"),
    "INNDT": (84, "All Non-insured Non-deposit Trust Companies in Indiana", "UBPPF863"),
    "INSVG": (308, "All Insured Savings Banks in Indiana", "UBPPF863"),
    "KSBKR": (142, "All Bankers Banks in Kansas", "UBPPF863"),
    "KSCOM": (254, "All Insured Commercial Banks in Kansas", "UBPPF863"),
    "KSSVG": (310, "All Insured Savings Banks in Kansas", "UBPPF863"),
    "KYBKR": (143, "All Bankers Banks in Kentucky", "UBPPF863"),
    "KYCOM": (255, "All Insured Commercial Banks in Kentucky", "UBPPF863"),
    "KYSVG": (311, "All Insured Savings Banks in Kentucky", "UBPPF863"),
    "LABKR": (144, "All Bankers Banks in Louisiana", "UBPPF863"),
    "LACOM": (256, "All Insured Commercial Banks in Louisiana", "UBPPF863"),
    "LASVG": (312, "All Insured Savings Banks in Louisiana", "UBPPF863"),
    "MACOM": (259, "All Insured Commercial Banks in Massachusetts", "UBPPF863"),
    "MANDT": (
        91,
        "All Non-insured Non-deposit Trust Companies in Massachusetts",
        "UBPPF863",
    ),
    "MASVG": (315, "All Insured Savings Banks in Massachusetts", "UBPPF863"),
    "MDCOM": (258, "All Insured Commercial Banks in Maryland", "UBPPF863"),
    "MDSVG": (314, "All Insured Savings Banks in Maryland", "UBPPF863"),
    "MECOM": (257, "All Insured Commercial Banks in Maine", "UBPPF863"),
    "MESVG": (313, "All Insured Savings Banks in Maine", "UBPPF863"),
    "MICOM": (260, "All Insured Commercial Banks in Michigan", "UBPPF863"),
    "MINDT": (
        92,
        "All Non-insured Non-deposit Trust Companies in Michigan",
        "UBPPF863",
    ),
    "MISVG": (316, "All Insured Savings Banks in Michigan", "UBPPF863"),
    "MNBKR": (150, "All Bankers Banks in Minnesota", "UBPPF863"),
    "MNCOM": (262, "All Insured Commercial Banks in Minnesota", "UBPPF863"),
    "MNNDT": (
        94,
        "All Non-insured Non-deposit Trust Companies in Minnesota",
        "UBPPF863",
    ),
    "MNSVG": (318, "All Insured Savings Banks in Minnesota", "UBPPF863"),
    "MOBKR": (152, "All Bankers Banks in Missouri", "UBPPF863"),
    "MOCOM": (264, "All Insured Commercial Banks in Missouri", "UBPPF863"),
    "MONDT": (
        96,
        "All Non-insured Non-deposit Trust Companies in Missouri",
        "UBPPF863",
    ),
    "MOSVG": (320, "All Insured Savings Banks in Missouri", "UBPPF863"),
    "MSCOM": (263, "All Insured Commercial Banks in Mississippi", "UBPPF863"),
    "MSSVG": (319, "All Insured Savings Banks in Mississippi", "UBPPF863"),
    "MTCOM": (265, "All Insured Commercial Banks in Montana", "UBPPF863"),
    "MTSVG": (321, "All Insured Savings Banks in Montana", "UBPPF863"),
    "NATIONAL": (2, "All banks in nation", "UBPPF866"),
    "NCCOM": (272, "All Insured Commercial Banks in North Carolina", "UBPPF863"),
    "NCNDT": (
        104,
        "All Non-insured Non-deposit Trust Companies in North Carolina",
        "UBPPF863",
    ),
    "NCSVG": (328, "All Insured Savings Banks in North Carolina", "UBPPF863"),
    "NDCOM": (273, "All Insured Commercial Banks in North Dakota", "UBPPF863"),
    "NDSVG": (329, "All Insured Savings Banks in North Dakota", "UBPPF863"),
    "NDT": (31, "All Non-insured Non-deposit Trust Companies", "UBPPF861"),
    "NECOM": (266, "All Insured Commercial Banks in Nebraska", "UBPPF863"),
    "NESVG": (322, "All Insured Savings Banks in Nebraska", "UBPPF863"),
    "NHCOM": (268, "All Insured Commercial Banks in New Hampshire", "UBPPF863"),
    "NHSVG": (324, "All Insured Savings Banks in New Hampshire", "UBPPF863"),
    "NJCOM": (269, "All Insured Commercial Banks in New Jersey", "UBPPF863"),
    "NJSVG": (325, "All Insured Savings Banks in New Jersey", "UBPPF863"),
    "NMCOM": (270, "All Insured Commercial Banks in New Mexico", "UBPPF863"),
    "NMSVG": (326, "All Insured Savings Banks in New Mexico", "UBPPF863"),
    "NVCOM": (267, "All Insured Commercial Banks in Nevada", "UBPPF863"),
    "NVCRC": (211, "All Credit Card Specialty Banks in Nevada", "UBPPF863"),
    "NVNDT": (99, "All Non-insured Non-deposit Trust Companies in Nevada", "UBPPF863"),
    "NVSVG": (323, "All Insured Savings Banks in Nevada", "UBPPF863"),
    "NYCOM": (271, "All Insured Commercial Banks in New York", "UBPPF863"),
    "NYNDT": (
        103,
        "All Non-insured Non-deposit Trust Companies in New York",
        "UBPPF863",
    ),
    "NYSVG": (327, "All Insured Savings Banks in New York", "UBPPF863"),
    "OHCOM": (274, "All Insured Commercial Banks in Ohio", "UBPPF863"),
    "OHNDT": (106, "All Non-insured Non-deposit Trust Companies in Ohio", "UBPPF863"),
    "OHSVG": (330, "All Insured Savings Banks in Ohio", "UBPPF863"),
    "OKBKR": (163, "All Bankers Banks in Oklahoma", "UBPPF863"),
    "OKCOM": (275, "All Insured Commercial Banks in Oklahoma", "UBPPF863"),
    "OKCRC": (219, "All Credit Card Specialty Banks in Oklahoma", "UBPPF863"),
    "OKNDT": (
        107,
        "All Non-insured Non-deposit Trust Companies in Oklahoma",
        "UBPPF863",
    ),
    "OKSVG": (331, "All Insured Savings Banks in Oklahoma", "UBPPF863"),
    "ORCOM": (276, "All Insured Commercial Banks in Oregon", "UBPPF863"),
    "ORNDT": (108, "All Non-insured Non-deposit Trust Companies in Oregon", "UBPPF863"),
    "ORSVG": (332, "All Insured Savings Banks in Oregon", "UBPPF863"),
    "PABKR": (165, "All Bankers Banks in Pennsylvania", "UBPPF863"),
    "PACOM": (277, "All Insured Commercial Banks in Pennsylvania", "UBPPF863"),
    "PANDT": (
        109,
        "All Non-insured Non-deposit Trust Companies in Pennsylvania",
        "UBPPF863",
    ),
    "PASVG": (333, "All Insured Savings Banks in Pennsylvania", "UBPPF863"),
    "PRCOM": (278, "All Insured Commercial Banks in Puerto Rico", "UBPPF863"),
    "RICOM": (279, "All Insured Commercial Banks in Rhode Island", "UBPPF863"),
    "RISVG": (335, "All Insured Savings Banks in Rhode Island", "UBPPF863"),
    "SCCOM": (280, "All Insured Commercial Banks in South Carolina", "UBPPF863"),
    "SCSVG": (336, "All Insured Savings Banks in South Carolina", "UBPPF863"),
    "SDCOM": (281, "All Insured Commercial Banks in South Dakota", "UBPPF863"),
    "SDNDT": (
        113,
        "All Non-insured Non-deposit Trust Companies in South Dakota",
        "UBPPF863",
    ),
    "SDSVG": (337, "All Insured Savings Banks in South Dakota", "UBPPF863"),
    "SVG": (19, "All insured savings banks", "UBPPF861"),
    "TNCOM": (282, "All Insured Commercial Banks in Tennessee", "UBPPF863"),
    "TNSVG": (338, "All Insured Savings Banks in Tennessee", "UBPPF863"),
    "TRST301": (62, "Trust Assets in excess of $100 billion", "UBPPF865"),
    "TRST302": (63, "Trust Assets between $10 billion and $100 billion", "UBPPF865"),
    "TRST303": (64, "Trust Assets between $1 billion and $10 billion", "UBPPF865"),
    "TRST304": (65, "Trust Assets between $250 million and $1 billion", "UBPPF865"),
    "TRST305": (66, "Trust Assets less than $250 million", "UBPPF865"),
    "TXBKR": (171, "All Bankers Banks in Texas", "UBPPF863"),
    "TXCOM": (283, "All Insured Commercial Banks in Texas", "UBPPF863"),
    "TXNDT": (115, "All Non-insured Non-deposit Trust Companies in Texas", "UBPPF863"),
    "TXSVG": (339, "All Insured Savings Banks in Texas", "UBPPF863"),
    "UTCOM": (284, "All Insured Commercial Banks in Utah", "UBPPF863"),
    "UTCRC": (228, "All Credit Card Specialty Banks in Utah", "UBPPF863"),
    "UTNDT": (116, "All Non-insured Non-deposit Trust Companies in Utah", "UBPPF863"),
    "VABKR": (175, "All Bankers Banks in Virginia", "UBPPF863"),
    "VACOM": (287, "All Insured Commercial Banks in Virginia", "UBPPF863"),
    "VACRC": (231, "All Credit Card Specialty Banks in Virginia", "UBPPF863"),
    "VANDT": (
        119,
        "All Non-insured Non-deposit Trust Companies in Virginia",
        "UBPPF863",
    ),
    "VASVG": (343, "All Insured Savings Banks in Virginia", "UBPPF863"),
    "VICOM": (286, "All Insured Commercial Banks in Virgin Islands", "UBPPF863"),
    "VTCOM": (285, "All Insured Commercial Banks in Vermont", "UBPPF863"),
    "VTSVG": (341, "All Insured Savings Banks in Vermont", "UBPPF863"),
    "WACOM": (288, "All Insured Commercial Banks in Washington", "UBPPF863"),
    "WASVG": (344, "All Insured Savings Banks in Washington", "UBPPF863"),
    "WIBKR": (178, "All Bankers Banks in Wisconsin", "UBPPF863"),
    "WICOM": (290, "All Insured Commercial Banks in Wisconsin", "UBPPF863"),
    "WINDT": (
        122,
        "All Non-insured Non-deposit Trust Companies in Wisconsin",
        "UBPPF863",
    ),
    "WISVG": (346, "All Insured Savings Banks in Wisconsin", "UBPPF863"),
    "WVCOM": (289, "All Insured Commercial Banks in West Virginia", "UBPPF863"),
    "WVNDT": (
        121,
        "All Non-insured Non-deposit Trust Companies in West Virginia",
        "UBPPF863",
    ),
    "WVSVG": (345, "All Insured Savings Banks in West Virginia", "UBPPF863"),
    "WYCOM": (291, "All Insured Commercial Banks in Wyoming", "UBPPF863"),
    "WYSVG": (347, "All Insured Savings Banks in Wyoming", "UBPPF863"),
}


def _records(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Index ``PGSelector`` rows by peer-group name."""
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = str(row.get("peergroupname", "")).strip()
        pid = row.get("peergroupid")
        if not name or pid in (None, ""):
            continue
        out[name] = {
            "peergroupid": int(pid),
            "description": str(row.get("peergroupdescription", "")).strip(),
            "conceptname": str(row.get("conceptname", "")).strip(),
        }
    return out


_STATIC_RECORDS: dict[str, dict[str, Any]] = {
    name: {"peergroupid": pid, "description": description, "conceptname": conceptname}
    for name, (pid, description, conceptname) in STATIC_PEER_GROUPS.items()
}


def fetch_peer_groups(cycle_id: str | int) -> dict[str, dict[str, Any]]:
    """Return the live peer-group registry for a reporting cycle, keyed by name.

    Each value is ``{"peergroupid", "description", "conceptname"}``. The router's
    ``PGSelector`` request with ``MinMembersReqd`` ``"0"`` returns the full,
    unfiltered list (~187 groups). On a failed or empty response the baked
    :data:`STATIC_PEER_GROUPS` snapshot is returned instead.
    """
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release
    from openbb_federal_reserve.utils.ubpr_report import _post

    def _producer() -> dict[str, dict[str, Any]]:
        """Fetch and index the full peer-group list for the cycle."""
        raw = _post(
            "PGSelector",
            {"ReportingCycleID": str(cycle_id), "MinMembersReqd": "0"},
        )
        records = _records(raw if isinstance(raw, list) else [])
        return records or dict(_STATIC_RECORDS)

    return cached(
        ("ubpr_peer_groups", str(cycle_id)),
        lambda: seconds_until_next_release("quarterly"),
        _producer,
    )


def _registry(cycle_id: str | int | None) -> dict[str, dict[str, Any]]:
    """Return the live registry for a cycle, or the static snapshot."""
    if cycle_id is None:
        return dict(_STATIC_RECORDS)
    return fetch_peer_groups(cycle_id)


def resolve_peer_group_id(name: str, *, cycle_id: str | int | None = None) -> int:
    """Resolve a peer-group name to its ``peergroupid``.

    Parameters
    ----------
    name : str
        The peer-group name (e.g. ``"1"``, ``"NATIONAL"``, ``"ALCOM"``).
    cycle_id : str | int | None
        The reporting cycle to resolve against; when given the live registry is
        used, otherwise the baked snapshot is used. An unknown name in the live
        registry falls back to the baked snapshot.

    Returns
    -------
    int
        The report URL's ``peergroupid``.
    """
    key = (name or "").strip().upper()
    record = _registry(cycle_id).get(key) or _STATIC_RECORDS.get(key)
    if record is None:
        raise ValueError(
            f"Unknown peer group '{name}'. Provide a peer-group name "
            "(e.g. '1', 'NATIONAL', 'ALCOM')."
        )
    return int(record["peergroupid"])


def peer_group_options(
    concepts: tuple[str, ...] | None = None,
) -> list[dict[str, str]]:
    """Build dropdown options from the baked snapshot, value = peer-group name.

    The option label expands to ``"name -- description"``. When ``concepts`` is
    given only peer groups in those ``conceptname`` categories are included.
    """
    options: list[dict[str, str]] = []
    for name, record in _STATIC_RECORDS.items():
        if concepts is not None and record["conceptname"] not in concepts:
            continue
        description = record["description"]
        label = f"{name} -- {description}" if description else name
        options.append({"label": label, "value": name})
    return options
