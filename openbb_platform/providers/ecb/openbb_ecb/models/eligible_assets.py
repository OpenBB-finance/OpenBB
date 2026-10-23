"""ECB Eurosystem Eligible Assets Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

_ASSET_TYPE = {
    "AT01": "Bond",
    "AT02": "Medium-term note",
    "AT03": "Treasury bill / commercial paper / certificate of deposit",
    "AT10": "EEA legislative covered bond",
    "AT11": "Asset-backed security (ABS)",
    "AT12": "Multi-cédulas",
    "AT13": "Non-EEA G10 legislative covered bond",
}
_ISSUER_GROUP = {
    "IG1": "Central bank",
    "IG2": "Central government",
    "IG3": "Corporate and other issuers",
    "IG4": "Credit institution (excluding agencies)",
    "IG5": "Regional/local government",
    "IG6": "Supranational issuer",
    "IG7": "Agency – non-credit institution",
    "IG8": "Agency – credit institution",
    "IG9": "Financial corporation other than credit institution",
    "IG11": "Public corporation",
}
_HAIRCUT_CATEGORY = {
    "L1A": "Category I – central government, EU, central banks",
    "L1B": "Category II – regional/local govt, agencies, supranationals, covered bonds",
    "L1C": "Category III – corporate and other issuers",
    "L1D": "Category IV – unsecured credit-institution debt",
    "L1E": "Category V – asset-backed securities",
}
_COUPON_DEFINITION = {"CD1": "Zero", "CD2": "Variable", "CD4": "Fixed"}
_COUNTRY = {
    "AT": "Austria",
    "AU": "Australia",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "CA": "Canada",
    "CH": "Switzerland",
    "CY": "Cyprus",
    "CZ": "Czechia",
    "DE": "Germany",
    "DK": "Denmark",
    "EE": "Estonia",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "GB": "United Kingdom",
    "GR": "Greece",
    "HR": "Croatia",
    "HU": "Hungary",
    "IE": "Ireland",
    "IS": "Iceland",
    "IT": "Italy",
    "JP": "Japan",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "MT": "Malta",
    "NL": "Netherlands",
    "NO": "Norway",
    "NZ": "New Zealand",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "SE": "Sweden",
    "SI": "Slovenia",
    "SK": "Slovakia",
    "US": "United States",
}
_ASSET_TYPE_BY_LABEL = {v: k for k, v in _ASSET_TYPE.items()}
_ISSUER_GROUP_BY_LABEL = {v: k for k, v in _ISSUER_GROUP.items()}
_HAIRCUT_BY_LABEL = {v: k for k, v in _HAIRCUT_CATEGORY.items()}


def _to_code(value: str | None, by_label: dict[str, str]) -> str | None:
    """Map a filter value back to its MID code."""
    return by_label.get(value, value) if value else None


def _decode_country(code: str, prefix: str) -> str:
    """Decode a ``<prefix><ISO2>`` code to a country name."""
    if code.upper().startswith(prefix) and len(code) >= len(prefix) + 2:
        iso2 = code[len(prefix) : len(prefix) + 2].upper()
        return _COUNTRY.get(iso2, code)
    return code


def _decode_reference_market(code: str) -> str:
    """Decode a ``RM<ISO2><nn>`` market code to ``<country> (<nn>)``."""
    if code.upper().startswith("RM") and len(code) >= 4:
        country = _COUNTRY.get(code[2:4].upper(), code[2:4])
        rest = code[4:]
        return f"{country} ({rest})" if rest else country
    return code


def _decode(row: dict) -> dict:
    """Replace ECB MID codes with human-readable labels."""
    out = dict(row)
    for field, mapping in (
        ("asset_type", _ASSET_TYPE),
        ("issuer_group", _ISSUER_GROUP),
        ("haircut_category", _HAIRCUT_CATEGORY),
        ("coupon_definition", _COUPON_DEFINITION),
    ):
        code = row.get(field)
        if code:
            out[field] = mapping.get(code, code)
    for field in ("issuer_residence", "guarantor_residence"):
        code = row.get(field)
        if code:
            out[field] = _decode_country(code, "IR")
    if row.get("reference_market"):
        out["reference_market"] = _decode_reference_market(row["reference_market"])
    return out


class ECBEligibleAssetsQueryParams(QueryParams):
    """ECB Eligible Assets Query."""

    __json_schema_extra__ = {
        "isin": {"multiple_items_allowed": True},
        "asset_type": {"choices": list(_ASSET_TYPE.values())},
        "haircut_category": {"choices": list(_HAIRCUT_CATEGORY.values())},
        "issuer_group": {"choices": list(_ISSUER_GROUP.values())},
        "currency": {
            "choices": ["EUR", "USD", "GBP", "JPY", "ATS", "DEM", "HRK", "SKK"]
        },
    }

    date: dateType | None = Field(
        default=None,
        description="Snapshot date. Defaults to the latest available business day.",
    )
    isin: str | None = Field(
        default=None, description="Filter by one or more ISIN codes."
    )
    asset_type: str | None = Field(
        default=None, description="Filter by asset type (e.g. 'Bond')."
    )
    haircut_category: str | None = Field(
        default=None, description="Filter by Eurosystem haircut (liquidity) category."
    )
    currency: str | None = Field(
        default=None, description="Filter by denomination currency (e.g. 'EUR')."
    )
    issuer_group: str | None = Field(
        default=None, description="Filter by issuer group (e.g. 'Central government')."
    )
    limit: int | None = Field(
        default=None, description="Limit the number of assets returned."
    )
    use_cache: bool = Field(
        default=True,
        description="If true, cache the parsed list on disk for the dataset TTL.",
    )


class ECBEligibleAssetsData(Data):
    """ECB Eligible Assets Data."""

    isin: str = Field(description="International Securities Identification Number.")
    asset_type: str | None = Field(default=None, description="Asset type.")
    haircut_category: str | None = Field(
        default=None, description="Eurosystem haircut (liquidity) category."
    )
    haircut: float | None = Field(
        default=None, description="Valuation haircut, in percent."
    )
    haircut_own_use: float | None = Field(
        default=None, description="Own-use valuation haircut, in percent."
    )
    reference_market: str | None = Field(default=None, description="Reference market.")
    currency: str | None = Field(default=None, description="Denomination currency.")
    coupon_rate: float | None = Field(default=None, description="Coupon rate, percent.")
    coupon_definition: str | None = Field(
        default=None, description="Coupon definition (Fixed, Variable, or Zero)."
    )
    issuance_date: dateType | None = Field(default=None, description="Issuance date.")
    maturity_date: dateType | None = Field(default=None, description="Maturity date.")
    issuer_name: str | None = Field(default=None, description="Issuer name.")
    issuer_residence: str | None = Field(
        default=None, description="Issuer country of residence."
    )
    issuer_group: str | None = Field(default=None, description="Issuer group.")
    guarantor_name: str | None = Field(default=None, description="Guarantor name.")
    guarantor_residence: str | None = Field(
        default=None, description="Guarantor country of residence."
    )
    covered_bond: str | None = Field(
        default=None, description="Potentially own-usable covered bond flag."
    )
    climate_factor: float | None = Field(default=None, description="Climate factor.")
    snapshot_date: dateType | None = Field(
        default=None, description="The date of the eligible-assets snapshot."
    )


class ECBEligibleAssetsFetcher(
    Fetcher[ECBEligibleAssetsQueryParams, list[ECBEligibleAssetsData]]
):
    """Fetch the Eurosystem eligible marketable assets list."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ECBEligibleAssetsQueryParams:
        """Transform query."""
        return ECBEligibleAssetsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ECBEligibleAssetsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the raw eligible-assets snapshot."""
        # pylint: disable=import-outside-toplevel
        from openbb_ecb.utils.data_cache import cached_records, make_key
        from openbb_ecb.utils.non_sdmx import fetch_eligible_assets

        async def loader() -> list[dict]:
            file_date, rows = await fetch_eligible_assets(query.date)
            for row in rows:
                row["snapshot_date"] = file_date
            return rows

        key = make_key(
            "eligible_assets",
            date=query.date.isoformat() if query.date else "latest",
        )
        return await cached_records(
            "eligible_assets", key, loader, use_cache=query.use_cache
        )

    @staticmethod
    def transform_data(
        query: ECBEligibleAssetsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[ECBEligibleAssetsData]:
        """Filter the snapshot, apply the limit, and validate."""
        isins = (
            {i.strip().upper() for i in query.isin.split(",")} if query.isin else None
        )
        asset_type = _to_code(query.asset_type, _ASSET_TYPE_BY_LABEL)
        haircut = _to_code(query.haircut_category, _HAIRCUT_BY_LABEL)
        issuer_group = _to_code(query.issuer_group, _ISSUER_GROUP_BY_LABEL)

        def keep(row: dict) -> bool:
            if isins and row.get("isin", "").upper() not in isins:
                return False
            if asset_type and row.get("asset_type") != asset_type:
                return False
            if haircut and row.get("haircut_category") != haircut:
                return False
            if query.currency and row.get("currency") != query.currency.upper():
                return False
            return not (issuer_group and row.get("issuer_group") != issuer_group)

        filtered = [row for row in data if keep(row)]
        if query.limit:
            filtered = filtered[: query.limit]
        if not filtered:
            raise EmptyDataError("No eligible assets matched the query.")
        return [ECBEligibleAssetsData.model_validate(_decode(d)) for d in filtered]
