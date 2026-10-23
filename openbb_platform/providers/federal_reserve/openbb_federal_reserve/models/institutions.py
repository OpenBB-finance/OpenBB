"""Federal Reserve NIC Institutions Model."""

from datetime import date
from typing import Any, Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

_CHARTER_TYPE_MAP = {
    "0": "Not available or not applicable",
    "110": "Government Agency / Government Sponsored Enterprise",
    "200": "Commercial Bank",
    "250": "Non-deposit Trust Company",
    "300": "Savings Bank",
    "310": "Savings & Loan Association",
    "320": "Cooperative Bank",
    "330": "Credit Union",
    "340": "Industrial Bank",
    "400": "Edge or Agreement Corporation",
    "500": "Holding Company",
    "550": "Insurance Broker, Agent, or Company",
    "610": "Employee Stock Ownership Plan/Trust",
    "700": "Securities Broker and/or Dealer",
    "710": "Utility Company or Electric Power Co-generator",
    "720": "Other Non-Depository Institution",
}

_ORGANIZATION_TYPE_MAP = {
    "0": "Not applicable",
    "1": "Corporation (stock)",
    "2": "General Partnership",
    "3": "Limited Partnership",
    "4": "Business Trust (fiduciary)",
    "5": "Sole Proprietorship",
    "6": "Mutual",
    "9": "Cooperative",
    "10": "Limited Liability Partnership",
    "11": "Limited Liability Company/Corporation",
    "12": "Estate Trust",
    "13": "Limited Liability Limited Partnership",
    "99": "Other",
}

_ENTITY_TYPE_MAP = {
    "AGB": "Agreement Corporation - Banking",
    "AGI": "Agreement Corporation - Investment",
    "BHC": "Bank Holding Company",
    "CPB": "Cooperative Bank",
    "CSA": "Covered Savings Institution",
    "DBR": "Domestic Branch of a Domestic Bank",
    "DEO": "Domestic Entity Other",
    "DPS": "Data Processing Servicer",
    "EBR": "Edge Corporation - Domestic Branch",
    "EDB": "Edge Corporation - Banking",
    "EDI": "Edge Corporation - Investment",
    "FBH": "Foreign Banking Organization as a BHC",
    "FBK": "Foreign Bank",
    "FBO": "Foreign Banking Organization",
    "FCU": "Federal Credit Union",
    "FEO": "Foreign Entity Other",
    "FHD": "Financial Holding Company / BHC",
    "FHF": "Financial Holding Company / FBO",
    "FNC": "Finance Company",
    "FSB": "Federal Savings Bank",
    "IBK": "International Bank of a U.S. Depository - Edge or Trust Co.",
    "IBR": "Foreign Branch of a U.S. Bank",
    "IHC": "Intermediate Holding Company",
    "IFB": "Insured Federal Branch of an FBO",
    "INB": "International Non-bank Subsidiary of a Domestic Entity",
    "ISB": "Insured State Branch of an FBO",
    "MTC": "Non-deposit Trust Company - Member",
    "NAT": "National Bank",
    "NMB": "Non-member Bank",
    "NTC": "Non-deposit Trust Company - Non-member",
    "NYI": "New York Investment Company",
    "PST": "Pseudo Twig - Non-U.S. Branch Managed by a U.S. Branch/Agency",
    "REP": "Representative Office",
    "SAL": "Savings & Loan Association",
    "SBD": "Securities Broker / Dealer",
    "SCU": "State Credit Union",
    "SLHC": "Savings and Loan Holding Company",
    "SMB": "State Member Bank",
    "SSB": "State Savings Bank",
    "TWG": "TWIG - Non-U.S. Branch Managed by a U.S. Branch/Agency",
    "UFA": "Uninsured Federal Agency of an FBO",
    "UFB": "Uninsured Federal Branch of an FBO",
}

_FIELD_MAP = {
    "#ID_RSSD": "rssd_id",
    "NM_LGL": "legal_name",
    "NM_SHORT": "short_name",
    "CITY": "city",
    "STATE_ABBR_NM": "state",
    "CNTRY_NM": "country",
    "ID_FDIC_CERT": "fdic_cert",
    "ID_OCC": "occ_id",
    "ID_LEI": "lei",
    "URL": "url",
}

_ID_FIELDS = {"fdic_cert", "occ_id", "lei", "url"}

_NIC_SENTINEL_DATES = {"99991231", "00000000", "0", ""}


def _parse_nic_date(value: Any) -> date | None:
    """Parse a NIC date (``YYYYMMDD`` int or ``MM/DD/YYYY HH:MM:SS``) to a date."""
    if value in (None, ""):
        return None
    text = str(value).strip()
    if text in _NIC_SENTINEL_DATES:
        return None
    parts: tuple[int, int, int] | None = None
    try:
        if "/" in text:
            month, day, year = (int(p) for p in text.split(" ", 1)[0].split("/"))
            parts = (year, month, day)
        elif len(text) == 8 and text.isdigit():
            parts = (int(text[:4]), int(text[4:6]), int(text[6:8]))
        if parts is not None:
            return date(*parts)
    except ValueError:
        return None
    return None


class FederalReserveInstitutionsQueryParams(QueryParams):
    """Federal Reserve NIC Institutions Query Parameters."""

    __json_schema_extra__ = {
        "status": {
            "x-widget_config": {
                "options": [
                    {"label": "Active institutions", "value": "active"},
                    {"label": "Closed institutions", "value": "closed"},
                    {"label": "Branches", "value": "branches"},
                ]
            }
        }
    }

    name: str | None = Field(
        default=None,
        description="Case-insensitive substring to match against institution names.",
    )
    rssd_id: str | None = Field(
        default=None,
        description="Filter to a specific institution by its RSSD identifier.",
    )
    ticker: str | None = Field(
        default=None,
        description="Find the parent holding company by its stock ticker.",
    )
    status: Literal["active", "closed", "branches"] = Field(
        default="active",
        description="Which NIC institution attributes file to search.",
    )


class FederalReserveInstitutionsData(Data):
    """Federal Reserve NIC Institutions Data."""

    rssd_id: str = Field(description="The institution's RSSD identifier.")
    legal_name: str | None = Field(default=None, description="The legal name.")
    short_name: str | None = Field(default=None, description="The short name.")
    entity_type_description: str | None = Field(
        default=None, description="The human-readable NIC entity type."
    )
    charter_type: str | None = Field(default=None, description="The NIC charter type.")
    organization_type: str | None = Field(
        default=None, description="The legal structure of the organization."
    )
    primary_federal_regulator: str | None = Field(
        default=None, description="The primary federal regulator of the institution."
    )
    is_bank_holding_company: str | None = Field(
        default=None, description="Whether the institution is a bank holding company."
    )
    is_financial_holding_company: str | None = Field(
        default=None,
        description="Whether the institution is a financial holding company.",
    )
    city: str | None = Field(default=None, description="The city.")
    state: str | None = Field(default=None, description="The state abbreviation.")
    country: str | None = Field(default=None, description="The country.")
    established_date: date | None = Field(
        default=None,
        description="The date the entity opened or otherwise came into existence.",
    )
    fdic_cert: str | None = Field(
        default=None, description="The FDIC certificate number."
    )
    occ_id: str | None = Field(default=None, description="The OCC charter identifier.")
    lei: str | None = Field(
        default=None, description="The Legal Entity Identifier (LEI)."
    )
    url: str | None = Field(default=None, description="The institution's website.")


class FederalReserveInstitutionsFetcher(
    Fetcher[
        FederalReserveInstitutionsQueryParams,
        list[FederalReserveInstitutionsData],
    ]
):
    """Federal Reserve NIC Institutions Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveInstitutionsQueryParams:
        """Transform the query params."""
        return FederalReserveInstitutionsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveInstitutionsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download and filter the NIC institution attributes."""
        from openbb_federal_reserve.utils.ffiec import fetch_institutions
        from openbb_federal_reserve.utils.ticker import resolve_ticker_to_rssd

        rssd_id = None
        if query.ticker:
            rssd_id = resolve_ticker_to_rssd(query.ticker)
            if not rssd_id:
                raise OpenBBError(
                    f"Could not resolve ticker '{query.ticker}' to a parent"
                    " holding company."
                )
        elif query.rssd_id and not query.name:
            rssd_id = query.rssd_id

        records = fetch_institutions(query.status)
        rows = [
            {k: (v.strip() if isinstance(v, str) else v) for k, v in r.items()}
            for r in records
        ]

        if rssd_id:
            rows = [r for r in rows if r.get("#ID_RSSD") == str(rssd_id).strip()]

        if query.name:
            needle = query.name.upper()
            rows = [
                r
                for r in rows
                if needle in (r.get("NM_LGL", "") or "").upper()
                or needle in (r.get("NM_SHORT", "") or "").upper()
            ]

        if not rows:
            raise EmptyDataError("No institutions matched the query.")

        return rows

    @staticmethod
    def transform_data(
        query: FederalReserveInstitutionsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveInstitutionsData]:
        """Curate the NIC attributes and translate coded fields to labels."""
        results: list[FederalReserveInstitutionsData] = []
        for row in data:
            mapped: dict[str, Any] = {}
            for source, target in _FIELD_MAP.items():
                value = row.get(source)
                if value in (None, ""):
                    continue
                if target in _ID_FIELDS and value == "0":
                    continue
                mapped[target] = value

            entity = row.get("ENTITY_TYPE")
            if entity:
                mapped["entity_type_description"] = _ENTITY_TYPE_MAP.get(entity, entity)

            charter = row.get("CHTR_TYPE_CD")
            if charter:
                mapped["charter_type"] = _CHARTER_TYPE_MAP.get(charter, charter)

            org = row.get("ORG_TYPE_CD")
            if org:
                mapped["organization_type"] = _ORGANIZATION_TYPE_MAP.get(org, org)

            regulator = row.get("PRIM_FED_REG")
            if regulator and regulator != "0":
                mapped["primary_federal_regulator"] = regulator

            bhc = row.get("BHC_IND")
            if bhc is not None:
                mapped["is_bank_holding_company"] = "No" if bhc == "0" else "Yes"

            fhc = row.get("FHC_IND")
            if fhc is not None:
                mapped["is_financial_holding_company"] = "No" if fhc == "0" else "Yes"

            established = _parse_nic_date(row.get("DT_OPEN")) or _parse_nic_date(
                row.get("DT_EXIST_CMNC")
            )
            if established is not None:
                mapped["established_date"] = established

            results.append(FederalReserveInstitutionsData.model_validate(mapped))
        return sorted(results, key=lambda r: r.rssd_id)
