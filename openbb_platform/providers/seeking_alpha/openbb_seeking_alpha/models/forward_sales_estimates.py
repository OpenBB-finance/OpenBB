"""Seeking Alpha Forward Sales Estimates Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.forward_sales_estimates import (
    ForwardSalesEstimatesData,
    ForwardSalesEstimatesQueryParams,
)
from openbb_core.provider.utils.helpers import amake_request
from openbb_seeking_alpha.utils.helpers import HEADERS, get_seekingalpha_id
from pydantic import Field, field_validator


class SAForwardSalesEstimatesQueryParams(ForwardSalesEstimatesQueryParams):
    """Seeking Alpha Forward Sales Estimates Query.

    Source: https://seekingalpha.com/earnings/earnings-calendar
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    period: Literal["annual", "quarter"] = Field(
        default="quarter",
        description="The reporting period.",
        json_schema_extra={"choices": ["annual", "quarter"]},
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def check_symbol(cls, value):
        """Check the symbol."""
        if not value:
            raise OpenBBError("Symbol is a required field for Seeking Alpha.")
        return value


class SAForwardSalesEstimatesData(ForwardSalesEstimatesData):
    """Seeking Alpha Forward Sales Estimates Data."""

    actual: Optional[int] = Field(
        default=None,
        description="Actual sales (revenue) for the period.",
    )
    period_growth: Optional[float] = Field(
        default=None,
        description="Estimated (or actual if reported) EPS growth for the period.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class SAForwardSalesEstimatesFetcher(
    Fetcher[
        SAForwardSalesEstimatesQueryParams,
        List[SAForwardSalesEstimatesData],
    ]
):
    """Seeking Alpha Forward Sales Estimates Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SAForwardSalesEstimatesQueryParams:
        """Transform the query."""
        return SAForwardSalesEstimatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SAForwardSalesEstimatesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Seeking Alpha endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.client import ClientSession

        tickers = query.symbol.split(",")  # type: ignore
        fp = query.period if query.period == "annual" else "quarterly"
        url = "https://seekingalpha.com/api/v3/symbol_data/estimates"
        querystring = {
            "estimates_data_items": "revenue_actual,revenue_consensus_low,revenue_consensus_mean,"
            "revenue_consensus_high,revenue_num_of_estimates",
            "period_type": fp,
            "relative_periods": "-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12",
        }

        async with ClientSession(trust_env=True) as session:
            kwargs = {"session": session}
            ids = {
                ticker: await get_seekingalpha_id(ticker, **kwargs)
                for ticker in tickers
            }
            querystring["ticker_ids"] = ("%2C").join(list(ids.values()))
            response = await amake_request(
                url, headers=HEADERS, params=querystring, session=session
            )
            estimates = response.get("estimates", {})  # type: ignore

        if not estimates:
            raise OpenBBError(f"No estimates data was returned for: {query.symbol}")
        output: Dict = {"ids": ids, "estimates": estimates}

        return output

    @staticmethod
    def transform_data(
        query: SAForwardSalesEstimatesQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> List[SAForwardSalesEstimatesData]:
        """Transform the data to the standard format."""
        tickers = query.symbol.split(",")  # type: ignore
        ids = data.get("ids", {})
        estimates = data.get("estimates", {})
        results: List[SAForwardSalesEstimatesData] = []
        for ticker in tickers:
            sa_id = str(ids.get(ticker, ""))
            if sa_id == "" or sa_id not in estimates:
                warn(f"Symbol Error: No data found for, {ticker}")
            seek_object = estimates.get(sa_id, {})
            if not seek_object:
                warn(f"No data found for {ticker}")
                continue
            items = len(seek_object.get("revenue_num_of_estimates"))
            if not items:
                warn(f"No data found for {ticker}")
                continue
            for i in range(0, items - 4):
                rev_estimates: Dict = {}
                rev_estimates["symbol"] = ticker
                num_estimates = seek_object["revenue_num_of_estimates"].get(str(i))
                if not num_estimates:
                    continue
                period = num_estimates[0].get("period", {})
                if period:
                    period_type = period.get("periodtypeid")
                    rev_estimates["calendar_year"] = period.get("calendaryear")
                    rev_estimates["calendar_period"] = (
                        "Q" + str(period.get("calendarquarter", ""))
                        if period_type == "quarterly"
                        else "FY"
                    )
                    rev_estimates["date"] = period.get("periodenddate").split("T")[0]
                    rev_estimates["fiscal_year"] = period.get("fiscalyear")
                    rev_estimates["fiscal_period"] = (
                        "Q" + str(period.get("fiscalquarter", ""))
                        if period_type == "quarterly"
                        else "FY"
                    )
                rev_estimates["number_of_analysts"] = num_estimates[0].get(
                    "dataitemvalue"
                )
                mean = seek_object["revenue_consensus_mean"].get(str(i))
                if mean:
                    mean = mean[0].get("dataitemvalue")
                    rev_estimates["mean"] = int(float(mean))
                actual = (
                    seek_object["revenue_actual"][str(i)][0].get("dataitemvalue")
                    if i < 1
                    else None
                )
                if actual:
                    rev_estimates["actual"] = int(float(actual))
                low = seek_object["revenue_consensus_low"].get(str(i))
                if low:
                    low = low[0].get("dataitemvalue")
                    rev_estimates["low_estimate"] = int(float(low))
                high = seek_object["revenue_consensus_high"].get(str(i))
                if high:
                    high = high[0].get("dataitemvalue")
                    rev_estimates["high_estimate"] = int(float(high))
                # Calculate the estimated growth percent.
                this = float(mean) if mean else None
                prev = None
                percent = None
                try:
                    prev = float(
                        seek_object["revenue"][str(i - 1)][0].get("dataitemvalue")
                    )
                except KeyError:
                    prev = float(
                        seek_object["revenue_consensus_mean"][str(i - 1)][0].get(
                            "dataitemvalue"
                        )
                    )
                if this and prev:
                    percent = (this - prev) / prev
                rev_estimates["period_growth"] = percent
                results.append(
                    SAForwardSalesEstimatesData.model_validate(rev_estimates)
                )

        return results
