"""OECD Balance of Payments (BOP6) Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.balance_of_payments import (
    BalanceOfPaymentsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_oecd.utils.constants import BOP_COUNTRIES
from pydantic import Field, field_validator

_MEASURE_HIER: dict[str, tuple[str, str | None, int]] = {
    "CA": ("Current account", None, 100),
    "G": ("Goods", "CA", 10),
    "G2": ("Net exports of goods under merchanting", "G", 1),
    "G21": ("Goods acquired under merchanting", "G2", 1),
    "G22": ("Goods sold under merchanting", "G2", 2),
    "S": ("Services", "CA", 20),
    "SA": ("Manufacturing services on physical inputs owned by others", "S", 10000),
    "SAY": (
        "Goods for processing in reporting economy; Goods returned, Goods received",
        "SA",
        1000,
    ),
    "SAZ": ("Goods for processing abroad; Goods sent, Goods returned", "SA", 2000),
    "SB": ("Maintenance and repair services n.i.e.", "S", 20000),
    "SC": ("Transport", "S", 30000),
    "SC1": ("Sea transport", "SC", 1000),
    "SC11": ("Sea transport; Passenger", "SC1", 100),
    "SC12": ("Sea transport; Freight", "SC1", 200),
    "SC13": ("Sea transport; Other than passenger and freight", "SC1", 300),
    "SC2": ("Air transport", "SC", 2000),
    "SC21": ("Air transport; Passenger", "SC2", 100),
    "SC22": ("Air transport; Freight", "SC2", 200),
    "SC23": ("Air transport; Other than passenger and freight", "SC2", 300),
    "SC3": ("Other modes of transport", "SC", 3000),
    "SC31": ("Other modes of transport; Passenger", "SC3", 100),
    "SC32": ("Other modes of transport; Freight", "SC3", 200),
    "SC33": ("Other modes of transport; Other than passenger and freight", "SC3", 300),
    "SC3_BIS": ("Extended classification of other modes of transport", "SC", 4000),
    "SC3A": ("Space transport", "SC3_BIS", 100),
    "SC3B": ("Rail transport", "SC3_BIS", 200),
    "SC3B1": ("Rail transport; Passenger", "SC3B", 10),
    "SC3B2": ("Rail transport; Freight", "SC3B", 20),
    "SC3B3": ("Rail transport; Other than passenger and freight", "SC3B", 30),
    "SC3C": ("Road transport", "SC3_BIS", 300),
    "SC3C1": ("Road transport; Passenger", "SC3C", 10),
    "SC3C2": ("Road transport; Freight", "SC3C", 20),
    "SC3C3": ("Road transport; Other than passenger and freight", "SC3C", 30),
    "SC3D": ("Inland waterway transport", "SC3_BIS", 400),
    "SC3D1": ("Inland waterway transport; Passenger", "SC3D", 10),
    "SC3D2": ("Inland waterway transport; Freight", "SC3D", 20),
    "SC3D3": (
        "Inland waterway transport; Other than passenger and freight",
        "SC3D",
        30,
    ),
    "SC3E": ("Pipeline transport", "SC3_BIS", 500),
    "SC3F": ("Electricity transmission", "SC3_BIS", 600),
    "SC3G": ("Other supporting and auxiliary transport services", "SC3_BIS", 700),
    "SC4": ("Postal and courier services", "SC", 5000),
    "SC41X": ("Memo item - Services; Postal services", "SC4", 100),
    "SC_BIS": (
        "Transport; All modes of transport; Passenger, freight and other",
        "S",
        40000,
    ),
    "SCA": ("All modes of transport; Passenger", "SC_BIS", 1000),
    "SCB": ("All modes of transport; Freight", "SC_BIS", 2000),
    "SCC": ("All modes of transport; Other than passenger and freight", "SC_BIS", 3000),
    "SCC1": (
        "All modes of transport; Other than passenger and freight; Other than Postal and courier services",
        "SCC",
        100,
    ),
    "SD": ("Travel", "S", 50000),
    "SDA": ("Travel; Business", "SD", 1000),
    "SDA1": (
        "Travel; Business; Acquisition of goods and services by border, seasonal, and other short-term workers",
        "SDA",
        100,
    ),
    "SDA2": (
        "Travel; Business; Other than acquisition of goods and services by border, seasonal,"
        " and other short-term workers",
        "SDA",
        200,
    ),
    "SDB": ("Travel; Personal", "SD", 2000),
    "SDB1": ("Travel; Personal; Health-related", "SDB", 100),
    "SDB2": ("Travel; Personal; Education-related", "SDB", 200),
    "SDB3": (
        "Travel; Personal; Other than heath-related and education-related",
        "SDB",
        300,
    ),
    "SE": ("Construction", "S", 60000),
    "SE1": ("Construction abroad", "SE", 1000),
    "SE2": ("Construction in the reporting economy", "SE", 2000),
    "SF": ("Insurance and pension services", "S", 70000),
    "SF1": ("Direct insurance", "SF", 1000),
    "SF11": ("Life insurance", "SF1", 100),
    "SF11Y": (
        "Gross life insurance premiums receivable (credits) and payable (debits)",
        "SF11",
        10,
    ),
    "SF11Z": (
        "Gross life insurance claims receivable (credits) and payable (debits)",
        "SF11",
        20,
    ),
    "SF12": ("Freight insurance", "SF1", 200),
    "SF12Y": (
        "Gross freight insurance premiums receivable (credits) and payable (debits)",
        "SF12",
        10,
    ),
    "SF12Z": (
        "Gross freight insurance claims receivable (credits) and payable (debits)",
        "SF12",
        20,
    ),
    "SF13": ("Direct insurance other than life and freight insurance", "SF1", 300),
    "SF13Y": (
        "Gross direct insurance (other than life and freight insurance) premiums receivable"
        " (credits) and payable (debits)",
        "SF13",
        10,
    ),
    "SF13Z": (
        "Gross direct insurance (other than life and freight insurance) claims receivable (credits) and payable (debits)",
        "SF13",
        20,
    ),
    "SF2": ("Reinsurance", "SF", 2000),
    "SF3": ("Auxiliary insurance services", "SF", 3000),
    "SF4": ("Pension and standardized guarantee services", "SF", 4000),
    "SF41": ("Pension services", "SF4", 100),
    "SF42": ("Standardized guarantee services", "SF4", 200),
    "SG": ("Financial services", "S", 80000),
    "SG1": (
        "Financial services explicitly charged and other financial services",
        "SG",
        1000,
    ),
    "SG2": (
        "Financial intermediation services indirectly measured (FISIM)",
        "SG",
        2000,
    ),
    "SH": ("Charges for the use of intellectual property n.i.e.", "S", 90000),
    "SH1": ("Franchises and trademarks licensing fees", "SH", 1000),
    "SH2": ("Licences for the use of outcomes of research and development", "SH", 2000),
    "SH3": ("Licences to reproduce and/or distribute computer software", "SH", 3000),
    "SH4": (
        "Licences to reproduce and/or distribute audio-visual and related products",
        "SH",
        4000,
    ),
    "SH41": (
        "Licences to reproduce and/or distribute audio-visual products",
        "SH4",
        100,
    ),
    "SH42": (
        "Licences to reproduce and/or distribute other than audio-visual products",
        "SH4",
        200,
    ),
    "SI": ("Telecommunications, computer, and information services", "S", 100000),
    "SI1": ("Telecommunications services", "SI", 1000),
    "SI2": ("Computer services", "SI", 2000),
    "SI21": ("Computer software", "SI2", 100),
    "SI21Z": ("Computer software; Software originals", "SI21", 10),
    "SI22": ("Computer services other than computer software", "SI2", 200),
    "SI3": ("Information services", "SI", 3000),
    "SI31": ("News agency services", "SI3", 100),
    "SI32": ("Information services other than news agency services", "SI3", 200),
    "SJ": ("Other business services", "S", 110000),
    "SJ1": ("Research and development services", "SJ", 1000),
    "SJ11": (
        "Work undertaken on a systematic basis to increase the stock of knowledge",
        "SJ1",
        100,
    ),
    "SJ111": (
        "Provision of customized and non-customized research and development services",
        "SJ11",
        10,
    ),
    "SJ112": (
        "Sale of proprietary rights arising from research and development",
        "SJ11",
        20,
    ),
    "SJ1121": ("Patents", "SJ112", 1),
    "SJ1122": ("Copyrights arising from research and development", "SJ112", 2),
    "SJ1123": ("Industrial processes and designs", "SJ112", 3),
    "SJ1124": (
        "Sales of proprietary rights arising from research and development other than patents,"
        " copyrights arising from research and development and industrial processes and designs",
        "SJ112",
        4,
    ),
    "SJ12": (
        "Research and development services other than work undertaken on a systematic basis"
        " to increase the stock of knowledge",
        "SJ1",
        200,
    ),
    "SJ2": ("Professional and management consulting services", "SJ", 2000),
    "SJ21": (
        "Legal, accounting, management consulting, and public relations services",
        "SJ2",
        100,
    ),
    "SJ211": ("Legal services", "SJ21", 10),
    "SJ212": (
        "Accounting, auditing, bookkeeping, and tax consulting services",
        "SJ21",
        20,
    ),
    "SJ213": (
        "Business and management consulting and public relations services",
        "SJ21",
        30,
    ),
    "SJ22": (
        "Advertising, market research, and public opinion polling services",
        "SJ2",
        200,
    ),
    "SJ22Z": (
        "Advertising, market research, and public opinion polling services;"
        " Convention, trade-fair and exhibition organization services",
        "SJ22",
        10,
    ),
    "SJ3": ("Technical, trade-related, and other business services", "SJ", 3000),
    "SJ31": (
        "Architectural, engineering, scientific, and other technical services",
        "SJ3",
        100,
    ),
    "SJ311": ("Architectural services", "SJ31", 10),
    "SJ312": ("Engineering services", "SJ31", 20),
    "SJ313": ("Scientific and other technical services", "SJ31", 30),
    "SJ32": (
        "Waste treatment and de-pollution, agricultural and mining services",
        "SJ3",
        200,
    ),
    "SJ321": ("Waste treatment and de-pollution", "SJ32", 10),
    "SJ322": ("Services incidental to agriculture, forestry and fishing", "SJ32", 20),
    "SJ323": ("Services incidental to mining, and oil and gas extraction", "SJ32", 30),
    "SJ32X": (
        "Memo grouping - Services; Services incidental to agriculture and mining",
        "SJ32",
        40,
    ),
    "SJ33": ("Operating leasing services", "SJ3", 300),
    "SJ34": ("Trade-related services", "SJ3", 400),
    "SJ35": ("Other business services n.i.e.", "SJ3", 500),
    "SJ35Z": (
        "Other business services n.i.e.; Employment services, i.e., search, placement and supply services of personnel",
        "SJ35",
        10,
    ),
    "SK": ("Personal, cultural, and recreational services", "S", 120000),
    "SK1": ("Audiovisual and related services", "SK", 1000),
    "SK11": ("Audio-visual services", "SK1", 100),
    "SK11Z": ("Audio-visual services; Audio-visual originals", "SK11", 10),
    "SK12": ("Artistic related services", "SK1", 200),
    "SK2": (
        "Personal, cultural, and recreational services other than audiovisual and related services",
        "SK",
        2000,
    ),
    "SK21": (
        "Personal, cultural, and recreational services other than audiovisual and related services; Health services",
        "SK2",
        100,
    ),
    "SK22": (
        "Personal, cultural, and recreational services other than audiovisual and related services; Education services",
        "SK2",
        200,
    ),
    "SK23": (
        "Personal, cultural, and recreational services other than audiovisual and related"
        " services; Heritage and recreational services",
        "SK2",
        300,
    ),
    "SK24": (
        "Personal, cultural, and recreational services other than audiovisual and related"
        " services; Personal services other than health, education and heritage and recreational services",
        "SK2",
        400,
    ),
    "SL": ("Government goods and services n.i.e.", "S", 130000),
    "SL1": ("Embassies and consulates", "SL", 1000),
    "SL2": ("Military units and agencies", "SL", 2000),
    "SL3": (
        "Government goods and services n.i.e other than embassies and consulates and military units and agencies",
        "SL",
        3000,
    ),
    "SN": ("Services not allocated", "S", 140000),
    "SD_BIS": ("Alternative presentation for travel", "S", 150000),
    "SD1": ("Travel; Goods", "SD_BIS", 1000),
    "SD2": ("Travel; Local transport services", "SD_BIS", 2000),
    "SD3": ("Travel; Accommodation services", "SD_BIS", 3000),
    "SD4": ("Travel; Food-serving services", "SD_BIS", 4000),
    "SD5": ("Travel; Other services", "SD_BIS", 5000),
    "SD5Z": ("Travel; Other services; Health services", "SD5", 10),
    "SD5Y": ("Travel; Other services; Education services", "SD5", 20),
    "SDZ": (
        "Tourism-related services in travel and passenger transport",
        "SD_BIS",
        6000,
    ),
    "S5": ("Total services transactions between related enterprises", "S", 160000),
    "SOX": ("Memo Grouping - Services; Commercial services", "S", 170000),
    "SOX1": (
        "Other commercial services - other services excluding Government goods and services n.i.e",
        "S",
        180000,
    ),
    "SPX1": (
        "Other services - Total services excluding Manufacturing services on physical inputs"
        " owned by others, Maintenance and repair services, Transport and Travel",
        "S",
        190000,
    ),
    "SPX4": (
        "Goods related services - Manufacturing services on physical inputs owned by others,"
        " + Maintenance and repair services",
        "S",
        200000,
    ),
    "IN1": ("Primary income", "CA", 30),
    "IN2": ("Secondary income", "CA", 40),
    "KA": ("Capital account", None, 200),
    "NP": (
        "Gross acquisitions / disposals of nonproduced nonfinancial assets",
        "KA",
        10,
    ),
    "D9": ("Capital transfers", "KA", 20),
    "FA": ("Financial account", None, 300),
    "FA_D_F": ("Direct investment", "FA", 10),
    "FA_D_FL": ("Direct investment; debt instruments (FDI)", "FA_D_F", 1),
    "FA_D_F5": (
        "Direct investment; equity and investment fund shares/units",
        "FA_D_F",
        2,
    ),
    "FA_P_F": ("Portfolio investment", "FA", 20),
    "FA_P_F3": ("Portfolio investment; debt securities", "FA_P_F", 1),
    "FA_P_F5": (
        "Portfolio investment; equity and investment fund shares/units",
        "FA_P_F",
        2,
    ),
    "FA_O_F": ("Other investment", "FA", 30),
    "FA_O_F2": ("Other investment; currency and deposits", "FA_O_F", 1),
    "FA_O_F4": ("Other investment; loans", "FA_O_F", 2),
    "FA_O_F4_S122": (
        "Other investment; loans; deposit taking corporations, except the central bank",
        "FA_O_F4",
        1,
    ),
    "FA_O_F519": ("Other investment; other equity", "FA_O_F", 3),
    "FA_O_F6": (
        "Other investment; insurance, pension and standardised guarantee schemes",
        "FA_O_F",
        4,
    ),
    "FA_O_F81": ("Other investment; trade credits and advances", "FA_O_F", 5),
    "FA_O_F89": (
        "Other investment; other accounts receivable/payable, excluding trade credits and advances",
        "FA_O_F",
        6,
    ),
    "FA_O_F12": ("Other investment; SDRs", "FA_O_F", 7),
    "FA_F_F7": ("Financial derivatives", "FA", 40),
    "FA_R_F_S121": ("Reserve assets", "FA", 50),
    "EO": ("Net errors and omissions", None, 400),
}


def _compute_level(code: str) -> int:
    """Walk parent chain to compute depth."""
    level = 0
    c = code
    while True:
        info = _MEASURE_HIER.get(c)
        if info is None or info[1] is None:
            break
        c = info[1]
        level += 1
    return level


_MEASURE_LEVEL: dict[str, int] = {code: _compute_level(code) for code in _MEASURE_HIER}


def _measure_sort_key(code: str) -> tuple[int, ...]:
    """Build a tuple of order values from root to this code for tree-walk sorting."""
    path: list[int] = []
    c: str | None = code
    while c is not None:
        info = _MEASURE_HIER.get(c)
        if info is None:
            break
        path.append(info[2])  # order
        c = info[1]  # parent
    return tuple(reversed(path))


_ENTRY_SORT: dict[str, int] = {
    "B": 0,
    "N": 0,  # Balance/Net first
    "C": 1,
    "A": 1,  # Credit/Assets second
    "D": 2,
    "L": 2,  # Debit/Liabilities third
}
_UNIT_SORT: dict[str, int] = {
    "USD_EXC": 0,
    "XDC": 1,
    "PT_B1GQ": 2,
    "PT_CA": 3,
    "PT_GS": 4,
}
_ENTRY_LABELS: dict[str, str] = {
    "A": "Assets",
    "B": "Balance",
    "C": "Credit",
    "D": "Debit",
    "L": "Liabilities",
    "N": "Net",
}
_UNIT_LABELS: dict[str, str] = {
    "USD_EXC": "US dollars",
    "XDC": "National currency",
    "PT_B1GQ": "Percentage of GDP",
    "PT_CA": "Percentage of current account",
    "PT_GS": "Percentage of goods and services",
}
_FREQ_MAP = {"annual": "A", "quarterly": "Q"}
_Q_MAP = {
    1: "Q1",
    2: "Q1",
    3: "Q1",
    4: "Q2",
    5: "Q2",
    6: "Q2",
    7: "Q3",
    8: "Q3",
    9: "Q3",
    10: "Q4",
    11: "Q4",
    12: "Q4",
}


def _format_start_period(d: dateType, freq: str) -> str:
    """Format a date as an SDMX startPeriod for the given frequency."""
    if freq == "A":
        return str(d.year)
    if freq == "Q":
        return f"{d.year}-{_Q_MAP[d.month]}"
    return f"{d.year}-{d.month:02d}"


def _format_end_period(d: dateType, freq: str) -> str:
    """Format a date as an SDMX endPeriod for the given frequency."""
    if freq == "A":
        return str(d.year)
    if freq == "Q":
        return f"{d.year}-{_Q_MAP[d.month]}"
    return f"{d.year}-{d.month:02d}"


class OECDBalanceOfPaymentsQueryParams(BalanceOfPaymentsQueryParams):
    """OECD Balance of Payments Query.

    Source: https://data-explorer.oecd.org/?lc=en
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": list(BOP_COUNTRIES) + ["all"],
        },
    }

    country: str = Field(
        default="united_states",
        description=QUERY_DESCRIPTIONS.get("country", ""),
    )
    frequency: Literal["annual", "quarterly"] = Field(
        default="quarterly",
        description="Frequency of the data.",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c: str):
        """Validate country."""
        return c.replace(" ", "_").strip().lower()


class OECDBalanceOfPaymentsData(Data):
    """OECD Balance of Payments Data.

    Each row is one observation from the OECD BOP6 presentation table.
    Hierarchy fields (parent, order, level) allow reconstruction of
    the full hierarchical table layout.
    """

    date: dateType | None = Field(
        default=None,
        description="The date representing the beginning of the reporting period.",
    )
    country: str | None = Field(
        default=None,
        description="Country name.",
    )
    title: str | None = Field(
        default=None,
        description="Name of the BOP measure.",
    )
    parent: str | None = Field(
        default=None,
        description="Name of the parent measure in the BOP6 hierarchy.",
    )
    order: int | None = Field(
        default=None,
        description="Unique sequential position in the hierarchical table (per date/country).",
    )
    level: int | None = Field(
        default=None,
        description="Depth in the hierarchy (0 = root, 1 = child of root, etc.).",
    )
    accounting_entry: str | None = Field(
        default=None,
        description="Accounting entry (Balance, Credit, Debit, Assets, Liabilities, Net).",
    )
    unit_measure: str | None = Field(
        default=None,
        description="Unit of measure.",
    )
    value: float | None = Field(
        default=None,
        description="Observation value.",
    )


class OECDBalanceOfPaymentsFetcher(
    Fetcher[OECDBalanceOfPaymentsQueryParams, list[OECDBalanceOfPaymentsData]]
):
    """OECD Balance of Payments Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> OECDBalanceOfPaymentsQueryParams:
        """Transform the query."""
        return OECDBalanceOfPaymentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: OECDBalanceOfPaymentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return raw data from the OECD BOP endpoint."""
        # pylint: disable=import-outside-toplevel
        from io import StringIO  # noqa
        from openbb_core.provider.utils.helpers import make_request
        from openbb_oecd.utils.metadata import OecdMetadata
        from pandas import read_csv, to_numeric  # type: ignore[import-untyped]

        meta = OecdMetadata()
        countries = meta.resolve_country_codes("DF_BOP", query.country)
        country_str = "+".join(countries) if countries else ""
        freq_code = _FREQ_MAP[query.frequency]
        dim_filter = (
            f"{country_str}"  # REF_AREA
            "."  # COUNTERPART_AREA (all)
            "."  # MEASURE (all)
            "."  # ACCOUNTING_ENTRY (all)
            "."  # FS_ENTRY (all)
            f".{freq_code}"  # FREQ
            ".USD_EXC"  # UNIT_MEASURE (all)
            ".Y"  # ADJUSTMENT (seasonally adjusted)
        )
        url = f"https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_BOP@DF_BOP,1.0/{dim_filter}"
        params: list[str] = []

        if query.start_date:
            params.append(
                f"startPeriod={_format_start_period(query.start_date, freq_code)}"
            )

        if query.end_date:
            params.append(f"endPeriod={_format_end_period(query.end_date, freq_code)}")

        if params:
            url += "?" + "&".join(params)

        headers = {
            "Accept": ("application/vnd.sdmx.data+csv; version=2.0.0; labels=both"),
            "User-Agent": "OpenBB/1.0",
        }
        response = make_request(url, headers=headers, timeout=120)
        response.raise_for_status()
        text = response.text

        if not text or not text.strip():
            raise OpenBBError(
                EmptyDataError(f"Empty response from OECD BOP. URL: {url}")
            )

        try:
            df = read_csv(StringIO(text))
        except Exception as exc:
            raise OpenBBError(
                f"Failed to parse OECD BOP CSV: {exc}\nURL: {url}"
            ) from exc

        if df.empty:
            raise OpenBBError(EmptyDataError(f"No BOP data rows. URL: {url}"))

        rename_map: dict[str, str] = {}

        for col in df.columns:
            if ": " in col:
                rename_map[col] = col.split(":")[0].strip()
            else:
                rename_map[col] = col

        df = df.rename(columns=rename_map)
        skip_cols = {
            "TIME_PERIOD",
            "OBS_VALUE",
            "DATAFLOW",
            "STRUCTURE",
            "STRUCTURE_ID",
            "ACTION",
        }

        for col in [
            c for c in df.columns if c not in skip_cols and df[c].dtype == object
        ]:
            sample = df[col].dropna().head(10)

            if sample.empty:
                continue

            if sample.str.contains(": ", regex=False).any():
                split = df[col].str.split(": ", n=1, expand=True)
                df[col] = split[0].str.strip()

                if split.shape[1] > 1:
                    df[f"{col}_label"] = split[1].str.strip()
                else:
                    df[f"{col}_label"] = df[col]

        if "OBS_VALUE" in df.columns:
            df["OBS_VALUE"] = to_numeric(df["OBS_VALUE"], errors="coerce")

        return df.to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: OECDBalanceOfPaymentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[OECDBalanceOfPaymentsData]:
        """Enrich each observation row with hierarchy metadata."""
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.helpers import oecd_date_to_python_date

        # Collect rows with their sort keys for global ordering.
        rows: list[tuple[tuple, dict]] = []

        for row in data:
            value = row.get("OBS_VALUE")

            if value is None or value == "":
                continue

            time_period = row.get("TIME_PERIOD", "")
            d = oecd_date_to_python_date(time_period)

            if d is None:
                continue

            if query.start_date and d < query.start_date:
                continue

            if query.end_date and d > query.end_date:
                continue

            measure = row.get("MEASURE", "")
            entry = row.get("ACCOUNTING_ENTRY", "")
            unit = row.get("UNIT_MEASURE", "")
            country_label = row.get("REF_AREA_label", row.get("REF_AREA", ""))
            # Look up hierarchy metadata from the DSD mapping.
            hier = _MEASURE_HIER.get(measure)

            if hier is not None:
                title, parent_code, _order = hier
            else:
                title = row.get("MEASURE_label", measure)
                parent_code = None

            level = _MEASURE_LEVEL.get(measure, 0)
            parent_hier = _MEASURE_HIER.get(parent_code) if parent_code else None
            parent_name = parent_hier[0] if parent_hier else None
            entry_name = _ENTRY_LABELS.get(
                entry, row.get("ACCOUNTING_ENTRY_label", entry)
            )
            unit_name = _UNIT_LABELS.get(unit, row.get("UNIT_MEASURE_label", unit))

            # Credit/Debit are children of Balance;
            # Assets/Liabilities are children of Net.
            if entry in ("B", "N"):
                row_level = level
                row_parent = parent_name
                row_title = title
            else:
                # C, D, A, L → one level deeper, parent is the measure title
                row_level = level + 1
                row_parent = title
                row_title = f"{title} - {entry_name}"

            # Build a composite sort key for depth-first tree ordering
            measure_path = _measure_sort_key(measure)
            entry_sort = _ENTRY_SORT.get(entry, 9)
            unit_sort = _UNIT_SORT.get(unit, 99)
            sort_key = (
                d or dateType.min,
                country_label or "",
                measure_path,
                entry_sort,
                unit_sort,
            )
            rows.append(
                (
                    sort_key,
                    {
                        "date": d,
                        "country": country_label,
                        "title": row_title,
                        "parent": row_parent,
                        "level": row_level,
                        "accounting_entry": entry_name,
                        "unit_measure": unit_name,
                        "value": float(value),
                    },
                )
            )

        rows.sort(key=lambda r: r[0])
        output: list[OECDBalanceOfPaymentsData] = []
        prev_group: tuple | None = None
        seq = 0

        for sort_key, rec in rows:
            group = (sort_key[0], sort_key[1])  # (date, country)

            if group != prev_group:
                seq = 0
                prev_group = group

            seq += 1
            rec["order"] = seq
            output.append(OECDBalanceOfPaymentsData.model_validate(rec))

        return sorted(
            output,
            key=lambda r: (r.date or dateType.min, r.country or "", r.order or 0),
        )
