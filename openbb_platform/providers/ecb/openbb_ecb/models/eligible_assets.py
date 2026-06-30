"""ECB Eurosystem Eligible Assets Model (collateral / MID).

The list of marketable assets eligible as Eurosystem monetary-policy collateral,
from the ECB Market Information Dissemination (MID) bulk CSV. No standard model
captures collateral-specific concepts (haircut category, own-use, climate
factor), so this is an ECB-specific model.
"""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class ECBEligibleAssetsQueryParams(QueryParams):
    """ECB Eligible Assets Query."""

    # Stable Eurosystem-coded categories of the MID eligible-assets dataset.
    __json_schema_extra__ = {
        "isin": {"multiple_items_allowed": True},
        "asset_type": {
            "choices": ["AT01", "AT02", "AT03", "AT10", "AT11", "AT12", "AT13"]
        },
        "haircut_category": {"choices": ["L1A", "L1B", "L1C", "L1D", "L1E"]},
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
        default=None, description="Filter by asset type code (e.g. 'AT03')."
    )
    haircut_category: str | None = Field(
        default=None, description="Filter by haircut category code (e.g. 'L1D')."
    )
    currency: str | None = Field(
        default=None, description="Filter by denomination currency (e.g. 'EUR')."
    )
    issuer_group: str | None = Field(
        default=None, description="Filter by issuer group code."
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
    asset_type: str | None = Field(default=None, description="Asset type code.")
    haircut_category: str | None = Field(
        default=None, description="Eurosystem haircut category."
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
        default=None, description="Coupon definition code."
    )
    issuance_date: dateType | None = Field(default=None, description="Issuance date.")
    maturity_date: dateType | None = Field(default=None, description="Maturity date.")
    issuer_name: str | None = Field(default=None, description="Issuer name.")
    issuer_residence: str | None = Field(
        default=None, description="Issuer country of residence."
    )
    issuer_group: str | None = Field(default=None, description="Issuer group code.")
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

        def keep(row: dict) -> bool:
            if isins and row.get("isin", "").upper() not in isins:
                return False
            if query.asset_type and row.get("asset_type") != query.asset_type:
                return False
            if (
                query.haircut_category
                and row.get("haircut_category") != query.haircut_category
            ):
                return False
            if query.currency and row.get("currency") != query.currency.upper():
                return False
            return not (
                query.issuer_group and row.get("issuer_group") != query.issuer_group
            )

        filtered = [row for row in data if keep(row)]
        if query.limit:
            filtered = filtered[: query.limit]
        if not filtered:
            raise EmptyDataError("No eligible assets matched the query.")
        return [ECBEligibleAssetsData.model_validate(d) for d in filtered]
