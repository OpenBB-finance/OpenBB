"""USDA ERS International Agricultural Productivity catalog, fetch, and parser."""

import csv
from io import StringIO

BASE_URL = "https://www.ers.usda.gov"
PRODUCT_PAGE = "data-products/international-agricultural-productivity"
MEDIA_PATH = (
    "/media/5403/machine-readable-and-long-format-file-of-tfp-indices-and"
    "-components-for-countries-regions-countries-grouped-by-income-level-and"
    "-the-world-1961-2023.csv"
)
DOWNLOAD_TIMEOUT = 120
YEAR_MIN = 1961
YEAR_MAX = 2023

GROUPINGS: dict[str, str] = {
    "sub_saharan_africa": "Sub-Saharan Africa",
    "latin_america_caribbean": "Latin America & Caribbean",
    "asia_pacific": "Asia & Pacific",
    "cwana": "Central/West Asia & North Africa",
    "europe": "Europe",
    "oceania": "Oceania",
    "north_america": "North America",
    "income_group": "Income group",
    "country_grouping": "Country grouping",
}

DEFAULT_GROUPING = "country_grouping"
DEFAULT_COUNTRY = 220
DEFAULT_MEASURE = "productivity_indices"

MEASURES: dict[str, dict] = {
    "productivity_indices": {
        "label": "Productivity indices (2015=100)",
        "columns": (
            ("TFP_Index", "TFP index (2015=100)"),
            ("Outall_Index", "Output index (2015=100)"),
            ("Input_Index", "Input index (2015=100)"),
            ("Land_Index", "Land input index (2015=100)"),
            ("Labor_Index", "Labor input index (2015=100)"),
            ("Capital_Index", "Capital input index (2015=100)"),
            ("Materials_Index", "Materials input index (2015=100)"),
        ),
    },
    "physical_quantities": {
        "label": "Physical quantities",
        "columns": (
            ("Outall_Q", "Total output ($1,000, 2015 prices)"),
            ("Outcrop_Q", "Crop output ($1,000, 2015 prices)"),
            ("Outanim_Q", "Animal output ($1,000, 2015 prices)"),
            ("Outfish_Q", "Aquaculture output ($1,000, 2015 prices)"),
            ("Land_Q", "Agricultural land (1,000 ha, rainfed-cropland-equiv.)"),
            ("Labor_Q", "Labor (1,000 persons in agriculture)"),
            ("Capital_Q", "Capital stock ($ million, 2015 prices)"),
            ("Fertilizer_Q", "Fertilizer (metric tons N, P, K)"),
            ("Feed_Q", "Feed (10^6 Mcal metabolizable energy)"),
            ("Cropland_Q", "Cropland (1,000 ha)"),
            ("Pasture_Q", "Permanent pasture (1,000 ha)"),
            ("IrrigArea_Q", "Area equipped for irrigation (1,000 ha)"),
        ),
    },
}

VARIABLE_HEADERS: dict[str, str] = {
    variable: header
    for spec in MEASURES.values()
    for variable, header in spec["columns"]
}

ENTITIES: tuple[tuple[int, str, str], ...] = (
    (1, "Nigeria", "sub_saharan_africa"),
    (2, "Benin", "sub_saharan_africa"),
    (3, "Côte d'Ivoire", "sub_saharan_africa"),
    (4, "Ghana", "sub_saharan_africa"),
    (5, "Guinea", "sub_saharan_africa"),
    (6, "Guinea-Bissau", "sub_saharan_africa"),
    (7, "Liberia", "sub_saharan_africa"),
    (8, "Sierra Leone", "sub_saharan_africa"),
    (9, "Togo", "sub_saharan_africa"),
    (10, "Cameroon", "sub_saharan_africa"),
    (11, "Central African Republic", "sub_saharan_africa"),
    (12, "Congo DR", "sub_saharan_africa"),
    (13, "Congo Republic", "sub_saharan_africa"),
    (14, "Equatorial Guinea", "sub_saharan_africa"),
    (15, "Gabon", "sub_saharan_africa"),
    (16, "Sao Tome and Principe", "sub_saharan_africa"),
    (17, "Burundi", "sub_saharan_africa"),
    (18, "Kenya", "sub_saharan_africa"),
    (19, "Rwanda", "sub_saharan_africa"),
    (20, "Tanzania", "sub_saharan_africa"),
    (21, "Uganda", "sub_saharan_africa"),
    (22, "Djibouti", "sub_saharan_africa"),
    (23, "Eritrea", "sub_saharan_africa"),
    (24, "Ethiopia", "sub_saharan_africa"),
    (25, "Somalia", "sub_saharan_africa"),
    (26, "South Sudan", "sub_saharan_africa"),
    (27, "Sudan", "sub_saharan_africa"),
    (28, "Burkina Faso", "sub_saharan_africa"),
    (29, "Cabo Verde", "sub_saharan_africa"),
    (30, "Chad", "sub_saharan_africa"),
    (31, "Gambia", "sub_saharan_africa"),
    (32, "Mali", "sub_saharan_africa"),
    (33, "Mauritania", "sub_saharan_africa"),
    (34, "Niger", "sub_saharan_africa"),
    (35, "Senegal", "sub_saharan_africa"),
    (36, "Angola", "sub_saharan_africa"),
    (37, "Comoros", "sub_saharan_africa"),
    (38, "Madagascar", "sub_saharan_africa"),
    (39, "Malawi", "sub_saharan_africa"),
    (40, "Mauritius", "sub_saharan_africa"),
    (41, "Mozambique", "sub_saharan_africa"),
    (42, "Zambia", "sub_saharan_africa"),
    (43, "Zimbabwe", "sub_saharan_africa"),
    (44, "Botswana", "sub_saharan_africa"),
    (45, "Eswatini", "sub_saharan_africa"),
    (46, "Lesotho", "sub_saharan_africa"),
    (47, "Namibia", "sub_saharan_africa"),
    (48, "South Africa", "sub_saharan_africa"),
    (49, "Belize", "latin_america_caribbean"),
    (50, "Costa Rica", "latin_america_caribbean"),
    (51, "El Salvador", "latin_america_caribbean"),
    (52, "Guatemala", "latin_america_caribbean"),
    (53, "Honduras", "latin_america_caribbean"),
    (54, "Mexico", "latin_america_caribbean"),
    (55, "Nicaragua", "latin_america_caribbean"),
    (56, "Panama", "latin_america_caribbean"),
    (57, "Bahamas", "latin_america_caribbean"),
    (58, "Cuba", "latin_america_caribbean"),
    (59, "Dominican Republic", "latin_america_caribbean"),
    (60, "Haiti", "latin_america_caribbean"),
    (61, "Jamaica", "latin_america_caribbean"),
    (62, "Lesser Antilles", "latin_america_caribbean"),
    (63, "Puerto Rico (U.S.)", "latin_america_caribbean"),
    (64, "Trinidad and Tobago", "latin_america_caribbean"),
    (65, "French Guiana (France)", "latin_america_caribbean"),
    (66, "Guyana", "latin_america_caribbean"),
    (67, "Suriname", "latin_america_caribbean"),
    (68, "Venezuela", "latin_america_caribbean"),
    (69, "Bolivia", "latin_america_caribbean"),
    (70, "Colombia", "latin_america_caribbean"),
    (71, "Ecuador", "latin_america_caribbean"),
    (72, "Peru", "latin_america_caribbean"),
    (73, "Brazil", "latin_america_caribbean"),
    (74, "Argentina", "latin_america_caribbean"),
    (75, "Chile", "latin_america_caribbean"),
    (76, "Paraguay", "latin_america_caribbean"),
    (77, "Uruguay", "latin_america_caribbean"),
    (78, "Japan", "asia_pacific"),
    (79, "Korea, Republic", "asia_pacific"),
    (80, "Taiwan", "asia_pacific"),
    (81, "China", "asia_pacific"),
    (82, "Korea, DPR", "asia_pacific"),
    (83, "Mongolia", "asia_pacific"),
    (84, "Brunei Darussalam", "asia_pacific"),
    (85, "Cambodia", "asia_pacific"),
    (86, "Indonesia", "asia_pacific"),
    (87, "Laos", "asia_pacific"),
    (88, "Malaysia", "asia_pacific"),
    (89, "Myanmar", "asia_pacific"),
    (90, "Philippines", "asia_pacific"),
    (91, "Thailand", "asia_pacific"),
    (92, "Timor-Leste", "asia_pacific"),
    (93, "Vietnam", "asia_pacific"),
    (94, "Fiji", "asia_pacific"),
    (95, "New Caledonia (France)", "asia_pacific"),
    (96, "Papua New Guinea", "asia_pacific"),
    (97, "Solomon Islands", "asia_pacific"),
    (98, "Vanuatu", "asia_pacific"),
    (99, "Micronesia", "asia_pacific"),
    (100, "Polynesia", "asia_pacific"),
    (101, "Bangladesh", "asia_pacific"),
    (102, "Bhutan", "asia_pacific"),
    (103, "India", "asia_pacific"),
    (104, "Nepal", "asia_pacific"),
    (105, "Pakistan", "asia_pacific"),
    (106, "Sri Lanka", "asia_pacific"),
    (107, "Armenia", "cwana"),
    (108, "Azerbaijan", "cwana"),
    (109, "Georgia", "cwana"),
    (110, "Bahrain", "cwana"),
    (111, "Cyprus", "cwana"),
    (112, "Iran", "cwana"),
    (113, "Iraq", "cwana"),
    (114, "Israel", "cwana"),
    (115, "West Bank and Gaza", "cwana"),
    (116, "Jordan", "cwana"),
    (117, "Kuwait", "cwana"),
    (118, "Lebanon", "cwana"),
    (119, "Oman", "cwana"),
    (120, "Qatar", "cwana"),
    (121, "Saudi Arabia", "cwana"),
    (122, "Syria", "cwana"),
    (123, "Turkey", "cwana"),
    (124, "United Arab Emirates", "cwana"),
    (125, "Yemen", "cwana"),
    (126, "Afghanistan", "cwana"),
    (127, "Kyrgyzstan", "cwana"),
    (128, "Tajikistan", "cwana"),
    (129, "Turkmenistan", "cwana"),
    (130, "Uzbekistan", "cwana"),
    (131, "Algeria", "cwana"),
    (132, "Egypt", "cwana"),
    (133, "Libya", "cwana"),
    (134, "Morocco", "cwana"),
    (135, "Tunisia", "cwana"),
    (136, "Belarus", "europe"),
    (137, "Kazakhstan", "europe"),
    (138, "Moldova", "europe"),
    (139, "Russian Federation", "europe"),
    (140, "Ukraine", "europe"),
    (141, "Albania", "europe"),
    (142, "Bulgaria", "europe"),
    (143, "Czechia", "europe"),
    (144, "Slovakia", "europe"),
    (145, "Hungary", "europe"),
    (146, "Poland", "europe"),
    (147, "Romania", "europe"),
    (148, "Croatia", "europe"),
    (149, "Slovenia", "europe"),
    (150, "Bosnia and Herzegovina", "europe"),
    (151, "North Macedonia", "europe"),
    (152, "Montenegro", "europe"),
    (153, "Serbia", "europe"),
    (154, "Estonia", "europe"),
    (155, "Latvia", "europe"),
    (156, "Lithuania", "europe"),
    (157, "Finland", "europe"),
    (158, "Iceland", "europe"),
    (159, "Norway", "europe"),
    (160, "Sweden", "europe"),
    (161, "Greece", "europe"),
    (162, "Italy", "europe"),
    (163, "Malta", "europe"),
    (164, "Portugal", "europe"),
    (165, "Spain", "europe"),
    (166, "Austria", "europe"),
    (167, "Belgium", "europe"),
    (168, "Luxembourg", "europe"),
    (169, "Denmark", "europe"),
    (170, "France", "europe"),
    (171, "Germany", "europe"),
    (172, "Ireland", "europe"),
    (173, "Netherlands", "europe"),
    (174, "Switzerland", "europe"),
    (175, "United Kingdom", "europe"),
    (176, "Australia", "oceania"),
    (177, "New Zealand", "oceania"),
    (178, "Canada", "north_america"),
    (179, "United States", "north_america"),
    (182, "SSA, Nigeria", "sub_saharan_africa"),
    (183, "SSA, Western", "sub_saharan_africa"),
    (184, "SSA, Central", "sub_saharan_africa"),
    (185, "SSA, Eastern", "sub_saharan_africa"),
    (186, "SSA, Horn", "sub_saharan_africa"),
    (187, "SSA, Sahel", "sub_saharan_africa"),
    (188, "SSA, Southern", "sub_saharan_africa"),
    (189, "SSA, SACU", "sub_saharan_africa"),
    (190, "SSA, Total", "sub_saharan_africa"),
    (191, "Central America", "latin_america_caribbean"),
    (192, "Caribbean", "latin_america_caribbean"),
    (193, "SA, Andean", "latin_america_caribbean"),
    (194, "SA, Brazil", "latin_america_caribbean"),
    (195, "SA, Southern Cone", "latin_america_caribbean"),
    (196, "LAC, Total", "latin_america_caribbean"),
    (197, "Asia, Developed", "asia_pacific"),
    (198, "NE Asia", "asia_pacific"),
    (199, "SE Asia", "asia_pacific"),
    (200, "Pacific", "asia_pacific"),
    (201, "South Asia", "asia_pacific"),
    (202, "ASIA, Total LDC", "asia_pacific"),
    (203, "ASIA, Total", "asia_pacific"),
    (204, "Central Asia", "cwana"),
    (205, "West Asia", "cwana"),
    (206, "North Africa", "cwana"),
    (207, "CWANA", "cwana"),
    (208, "Europe, Eastern", "europe"),
    (209, "Europe, Central", "europe"),
    (210, "Europe, Northern", "europe"),
    (211, "Europe, Southern", "europe"),
    (212, "Europe, Western", "europe"),
    (213, "EUROPE, Total", "europe"),
    (214, "OCEANIA", "oceania"),
    (215, "NORTH AMERICA", "north_america"),
    (217, "Industrialized Countries", "country_grouping"),
    (218, "Developing Countries", "country_grouping"),
    (220, "World", "country_grouping"),
    (223, "Low income", "income_group"),
    (224, "Lower-middle income", "income_group"),
    (225, "Upper-middle income", "income_group"),
    (226, "Upper-middle income, excluding China", "income_group"),
    (227, "China", "income_group"),
    (228, "High income", "income_group"),
    (231, "Ethiopia, former", "sub_saharan_africa"),
    (232, "Sudan, former", "sub_saharan_africa"),
    (233, "Czechoslovakia, former", "europe"),
    (234, "Belgium-Luxembourg", "europe"),
    (235, "Serbia and Montenegro", "europe"),
    (236, "Yugoslavia, former", "europe"),
    (237, "Former Soviet Union", "country_grouping"),
    (238, "Transition countries", "country_grouping"),
    (239, "EU14 (includes E&W Germany, excludes UK)", "country_grouping"),
    (240, "EU27 (27 countries as of 2021 excludes UK)", "country_grouping"),
    (241, "OECD (38 countries as of 2021)", "country_grouping"),
    (242, "G20 (19 countries 2021)", "country_grouping"),
)

ENTITY_LABEL: dict[int, str] = {order: label for order, label, _ in ENTITIES}
ENTITY_GROUPING: dict[int, str] = {order: grouping for order, _, grouping in ENTITIES}


def grouping_options() -> list[dict]:
    """Build the labeled grouping options for the widget's grouping selector.

    Returns
    -------
    list[dict]
        Label/value option dictionaries, one per grouping bucket.
    """
    return [{"label": label, "value": key} for key, label in GROUPINGS.items()]


def measure_options() -> list[dict]:
    """Build the labeled measure-family options for the widget's measure selector.

    Returns
    -------
    list[dict]
        Label/value option dictionaries, one per measure family.
    """
    return [{"label": spec["label"], "value": key} for key, spec in MEASURES.items()]


def entity_options(grouping: str) -> list[dict]:
    """List a grouping's entities as labeled options keyed by dataset order.

    Parameters
    ----------
    grouping : str
        Grouping key from GROUPINGS.

    Returns
    -------
    list[dict]
        Label/value option dictionaries, the value being the unique dataset
        order that disambiguates entities sharing a name, e.g. the country
        'China' (order 81) from the income aggregate 'China' (order 227).
    """
    return [
        {"label": label, "value": order}
        for order, label, bucket in ENTITIES
        if bucket == grouping
    ]


def parse_entity(text: str, order: int) -> list[dict]:
    """Parse the long-format CSV into one entity's observation records.

    Parameters
    ----------
    text : str
        Decoded long-format CSV text of the release file.
    order : int
        Dataset order of the entity to keep.

    Returns
    -------
    list[dict]
        Records with year, variable, and value keys, for the entity's index
        and quantity variables. Rows of other entities or variables, blank
        years, and non-numeric values are skipped.
    """
    target = str(order)
    records: list[dict] = []
    for row in csv.DictReader(StringIO(text)):
        if (row.get("Order") or "").strip() != target:
            continue
        variable = (row.get("Variable") or "").strip()
        if variable not in VARIABLE_HEADERS:
            continue
        year_raw = (row.get("Year") or "").strip()
        if not (len(year_raw) == 4 and year_raw.isdigit()):
            continue
        try:
            value = float((row.get("Value") or "").strip())
        except ValueError:
            continue
        records.append({"year": int(year_raw), "variable": variable, "value": value})
    return records


async def _adownload() -> bytes:
    """Download the release CSV as raw bytes with an extended timeout.

    Returns
    -------
    bytes
        The raw file content of the 18 MB long-format CSV.
    """
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.helpers import amake_request

    url = f"{BASE_URL}{MEDIA_PATH}"

    async def read_bytes(response, _session) -> bytes:
        if response.status != 200:
            raise OpenBBError(
                f"ERS request failed with status {response.status} -> {url}"
            )
        return await response.read()

    result = await amake_request(
        url,
        timeout=DOWNLOAD_TIMEOUT,
        response_callback=read_bytes,  # ty: ignore[invalid-argument-type]
    )
    return result  # ty: ignore[invalid-return-type]


async def afetch_dataset() -> str:
    """Download and decode the long-format CSV through the ERS disk cache.

    Returns
    -------
    str
        The decoded long-format CSV text of the current release.
    """
    from openbb_government_us.usda.utils.ers_client import DEFAULT_FILE_TTL, get_cache

    key = f"file:{MEDIA_PATH}"
    with get_cache() as cache:
        cached = cache.get(key)
        if cached is not None:
            return cached.decode("utf-8-sig", errors="replace")
    content = await _adownload()
    with get_cache() as cache:
        cache.set(key, content, expire=DEFAULT_FILE_TTL)
    return content.decode("utf-8-sig", errors="replace")


async def afetch_entity(order: int) -> list[dict]:
    """Download the release CSV and parse one entity's observation records.

    Parameters
    ----------
    order : int
        Dataset order of the entity to keep.

    Returns
    -------
    list[dict]
        Records from parse_entity for the selected entity.
    """
    text = await afetch_dataset()
    return parse_entity(text, order)
