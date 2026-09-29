"""Curated registry of published BLS Producer Price Index tables."""

from typing import Literal, TypedDict

_BASE = "https://www.bls.gov/web"


class TableEntry(TypedDict):
    """Metadata describing one published BLS table artifact."""

    program: str
    category: str
    label: str
    format: Literal["xlsx", "htm"]
    url: str


PPI_RELATIVE_IMPORTANCE_TABLES: dict[str, TableEntry] = {
    "ppi-fdallrel": {
        "program": "ppi",
        "category": "final_demand",
        "label": "PPI Final Demand relative importance — by individual commodities",
        "format": "xlsx",
        "url": f"{_BASE}/ppi/ppi-fdallrel.xlsx",
    },
    "ppi-fdgrouprel": {
        "program": "ppi",
        "category": "final_demand",
        "label": "PPI Final Demand relative importance — by component series",
        "format": "xlsx",
        "url": f"{_BASE}/ppi/ppi-fdgrouprel.xlsx",
    },
    "ppi-idcallrel": {
        "program": "ppi",
        "category": "intermediate_demand_commodity",
        "label": "PPI Intermediate Demand by Commodity Type relative importance — individual",
        "format": "xlsx",
        "url": f"{_BASE}/ppi/ppi-idcallrel.xlsx",
    },
    "ppi-idcgrouprel": {
        "program": "ppi",
        "category": "intermediate_demand_commodity",
        "label": "PPI Intermediate Demand by Commodity Type relative importance — component",
        "format": "xlsx",
        "url": f"{_BASE}/ppi/ppi-idcgrouprel.xlsx",
    },
    "ppi-idpallrel": {
        "program": "ppi",
        "category": "intermediate_demand_flow",
        "label": "PPI Intermediate Demand by Production Flow relative importance — individual",
        "format": "xlsx",
        "url": f"{_BASE}/ppi/ppi-idpallrel.xlsx",
    },
    "ppi-idpgrouprel": {
        "program": "ppi",
        "category": "intermediate_demand_flow",
        "label": "PPI Intermediate Demand by Production Flow relative importance — component",
        "format": "xlsx",
        "url": f"{_BASE}/ppi/ppi-idpgrouprel.xlsx",
    },
    "ppi-comrlp": {
        "program": "ppi",
        "category": "commodity",
        "label": "PPI Commodities relative importance — all levels",
        "format": "xlsx",
        "url": f"{_BASE}/ppi/ppi-comrlp.xlsx",
    },
    "ppi-weprel": {
        "program": "ppi",
        "category": "service_construction",
        "label": "PPI Wherever-Provided Services and Construction relative importance",
        "format": "xlsx",
        "url": f"{_BASE}/ppi/ppi-weprel.xlsx",
    },
}

PPI_RELATIVE_IMPORTANCE_CANONICAL: dict[str, str] = {
    "final_demand": "ppi-fdallrel",
    "intermediate_demand_commodity": "ppi-idcallrel",
    "intermediate_demand_flow": "ppi-idpallrel",
    "commodity": "ppi-comrlp",
    "service_construction": "ppi-weprel",
}


PPI_SEASONAL_FACTOR_TABLES: dict[str, TableEntry] = {
    "ppi-fdidsf": {
        "program": "ppi",
        "category": "fd_id",
        "label": "PPI FD-ID aggregation index seasonal factors — previous five years",
        "format": "htm",
        "url": f"{_BASE}/ppi/ppi-fdidsf.htm",
    },
    "ppi-commsf": {
        "program": "ppi",
        "category": "commodity",
        "label": "PPI Commodity index seasonal factors — previous five years",
        "format": "htm",
        "url": f"{_BASE}/ppi/ppi-commsf.htm",
    },
    "ppi-seafac": {
        "program": "ppi",
        "category": "forecast",
        "label": "PPI Commodity forecasting seasonal factors — current year",
        "format": "htm",
        "url": f"{_BASE}/ppi/ppi-seafac.htm",
    },
}

PPI_SEASONAL_FACTOR_CANONICAL: dict[str, str] = {
    "fd_id": "ppi-fdidsf",
    "commodity": "ppi-commsf",
    "forecast": "ppi-seafac",
}
