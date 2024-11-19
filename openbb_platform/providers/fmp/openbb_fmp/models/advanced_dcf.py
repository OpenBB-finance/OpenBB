"""Advanced Dcf Model."""

import asyncio
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.advanced_dcf import (
    AdvancedDcfData,
    AdvancedDcfQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request, to_snake_case
from openbb_fmp.utils.helpers import create_url
from pydantic import Field


class FMPAdvancedDcfQueryParams(AdvancedDcfQueryParams):
    """Advanced Dcf Query Parameters.

    Source: https://financialmodelingprep.com/api/v4/advanced_discounted_cash_flow?symbol=AAPL
    Source: https://financialmodelingprep.com/api/v4/advanced_levered_discounted_cash_flow?symbol=AAPL
    """


class FMPAdvancedDcfData(AdvancedDcfData):
    """Advanced Dcf Data Model."""

    __alias_dict__ = {
        "stock_price": "Stock Price",
    }
    ebitda: Optional[float] = Field(
        default=None,
        description="Earnings Before Interest, Taxes, Depreciation, and Amortization, indicating company profitability.",
    )
    ebitda_percentage: Optional[float] = Field(
        default=None, description="Percentage of EBITDA relative to revenue."
    )
    ebit: Optional[float] = Field(
        default=None,
        description="Earnings Before Interest and Taxes, representing operating profit after costs.",
    )
    ebit_percentage: Optional[float] = Field(
        default=None, description="Percentage of EBIT relative to revenue."
    )
    depreciation: Optional[float] = Field(
        default=None,
        description="Depreciation and amortization expenses spread over asset lifespan.",
    )
    depreciation_percentage: Optional[float] = Field(
        default=None, description="Percentage of depreciation relative to revenue."
    )
    total_cash: Optional[float] = Field(
        default=None, description="Total cash held by the company."
    )
    total_cash_percentage: Optional[float] = Field(
        default=None, description="Percentage of total cash relative to revenue."
    )
    receivables: Optional[float] = Field(
        default=None,
        description="Accounts receivable, representing amounts owed from sales.",
    )
    receivables_percentage: Optional[float] = Field(
        default=None, description="Percentage of receivables relative to revenue."
    )
    inventories: Optional[float] = Field(
        default=None,
        description="Inventory, including raw materials, work-in-progress, and finished goods not yet sold.",
    )
    inventories_percentage: Optional[float] = Field(
        default=None, description="Percentage of inventory relative to revenue."
    )
    payable: Optional[float] = Field(
        default=None,
        description="Accounts payable, representing amounts owed for purchased goods or services.",
    )
    payable_percentage: Optional[float] = Field(
        default=None, description="Percentage of payable relative to revenue."
    )
    tax_rate_cash: Optional[float] = Field(
        default=None,
        description="Cash tax rate, representing the effective tax rate paid by the company.",
    )
    ebiat: Optional[float] = Field(
        default=None,
        description="Earnings Before Interest After Taxes, representing operating earnings after tax.",
    )
    ufcf: Optional[float] = Field(
        default=None,
        description="Unlevered Free Cash Flow, representing cash flow after capex and working capital changes.",
    )
    sum_pv_ufcf: Optional[float] = Field(
        default=None,
        description="Total present value of future unlevered free cash flows.",
    )
    operating_cash_flow: Optional[float] = Field(
        default=None,
        description="Operating cash flow generated from core business activities.",
    )
    pv_lfcf: Optional[float] = Field(
        default=None,
        description="Present value of levered free cash flow, discounted at appropriate rate.",
    )
    sum_pv_lfcf: Optional[float] = Field(
        default=None, description="Total present value of future levered cash flows."
    )
    free_cash_flow: Optional[float] = Field(
        default=None,
        description="Levered Free Cash Flow, representing cash flow after interest and capex.",
    )
    operating_cash_flow_percentage: Optional[float] = Field(
        default=None,
        description="Percentage of operating cash flow relative to revenue.",
    )


class FMPAdvancedDcfFetcher(
    Fetcher[
        FMPAdvancedDcfQueryParams,
        List[FMPAdvancedDcfData],
    ]
):
    """Fetches and transforms data from the Advanced Dcf endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPAdvancedDcfQueryParams:
        """Transform the query params."""
        return FMPAdvancedDcfQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPAdvancedDcfQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Advanced Dcf endpoint."""
        symbols = query.symbol.split(",")
        results: List[Dict] = []
        debt = query.debt

        async def get_one(symbol):
            """Get data for the given symbol."""
            api_key = credentials.get("fmp_api_key") if credentials else ""
            if debt:
                url = create_url(
                    4,
                    "advanced_levered_discounted_cash_flow",
                    api_key,
                    query,
                    exclude=["debt"],
                )
            else:
                url = create_url(
                    4,
                    "advanced_discounted_cash_flow",
                    api_key,
                    query,
                    exclude=["debt"],
                )
            result = await amake_request(url, **kwargs)
            if not result or len(result) == 0:
                warn(f"Symbol Error: No data found for symbol {symbol}")
            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])
        results = [
            {to_snake_case(key): value for key, value in d.items()}
            for d in results
            if isinstance(d, dict)
        ]
        if not results:
            raise EmptyDataError("No data returned for the given symbol.")

        return results

    @staticmethod
    def transform_data(
        query: FMPAdvancedDcfQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPAdvancedDcfData]:
        """Return the transformed data."""
        return [FMPAdvancedDcfData(**d) for d in data]
