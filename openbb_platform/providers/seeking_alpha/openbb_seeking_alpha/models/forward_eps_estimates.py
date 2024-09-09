"""Seeking Alpha Forward EPS Estimates Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.forward_eps_estimates import (
    ForwardEpsEstimatesData,
    ForwardEpsEstimatesQueryParams,
)
from openbb_core.provider.utils.helpers import amake_request
from openbb_seeking_alpha.utils.helpers import HEADERS, get_seekingalpha_id
from pydantic import Field, field_validator


class SAForwardEpsEstimatesQueryParams(ForwardEpsEstimatesQueryParams):
    """Seeking Alpha Forward EPS Estimates Query.

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


class SAForwardEpsEstimatesData(ForwardEpsEstimatesData):
    """Seeking Alpha Forward EPS Estimates Data."""

    normalized_actual: Optional[float] = Field(
        default=None,
        description="Actual normalized EPS.",
    )
    period_growth: Optional[float] = Field(
        default=None,
        description="Estimated (or actual if reported) EPS growth for the period.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    low_estimate_gaap: Optional[float] = Field(
        default=None,
        description="Estimated GAAP EPS low for the period.",
    )
    high_estimate_gaap: Optional[float] = Field(
        default=None,
        description="Estimated GAAP EPS high for the period.",
    )
    mean_gaap: Optional[float] = Field(
        default=None,
        description="Estimated GAAP EPS mean for the period.",
    )
    gaap_actual: Optional[float] = Field(
        default=None,
        description="Actual GAAP EPS.",
    )


class SAForwardEpsEstimatesFetcher(
    Fetcher[
        SAForwardEpsEstimatesQueryParams,
        List[SAForwardEpsEstimatesData],
    ]
):
    """Seeking Alpha Forward EPS Estimates Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SAForwardEpsEstimatesQueryParams:
        """Transform the query."""
        return SAForwardEpsEstimatesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SAForwardEpsEstimatesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Seeking Alpha endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.client import ClientSession

        tickers = query.symbol.split(",")  # type: ignore
        fp = query.period if query.period == "annual" else "quarterly"
        url = "https://seekingalpha.com/api/v3/symbol_data/estimates"
        querystring: Dict = {
            "estimates_data_items": "eps_normalized_actual,eps_normalized_consensus_low,eps_normalized_consensus_mean,"
            "eps_normalized_consensus_high,eps_normalized_num_of_estimates,"
            "eps_gaap_actual,eps_gaap_consensus_low,eps_gaap_consensus_mean,eps_gaap_consensus_high,",
            "period_type": fp,
            "relative_periods": "-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11",
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

        estimates: Dict = response.get("estimates", {})  # type: ignore
        if not estimates:
            raise OpenBBError(f"No estimates data was returned for: {query.symbol}")

        output: Dict = {"ids": ids, "estimates": estimates}

        return output

    @staticmethod
    def transform_data(
        query: SAForwardEpsEstimatesQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> List[SAForwardEpsEstimatesData]:
        """Transform the data to the standard format."""
        tickers = query.symbol.split(",")  # type: ignore
        ids = data.get("ids", {})
        estimates = data.get("estimates", {})
        results: List[SAForwardEpsEstimatesData] = []
        for ticker in tickers:
            sa_id = str(ids.get(ticker, ""))
            if sa_id == "" or sa_id not in estimates:
                warn(f"Symbol Error: No data found for, {ticker}")
                continue

            seek_object = estimates.get(sa_id, {})
            if not seek_object:
                warn(f"No data found for {ticker}")
                continue
            items = len(seek_object.get("eps_normalized_num_of_estimates"))
            if not items:
                warn(f"No data found for {ticker}")
                continue
            for i in range(0, items - 4):
                eps_estimates: Dict = {}
                eps_estimates["symbol"] = ticker
                num_estimates = seek_object["eps_normalized_num_of_estimates"].get(
                    str(i)
                )
                if not num_estimates:
                    continue
                period = num_estimates[0].get("period", {})
                if period:
                    period_type = period.get("periodtypeid")
                    eps_estimates["calendar_year"] = period.get("calendaryear")
                    eps_estimates["calendar_period"] = (
                        "Q" + str(period.get("calendarquarter", ""))
                        if period_type == "quarterly"
                        else "FY"
                    )
                    eps_estimates["date"] = period.get("periodenddate").split("T")[0]
                    eps_estimates["fiscal_year"] = period.get("fiscalyear")
                    eps_estimates["fiscal_period"] = (
                        "Q" + str(period.get("fiscalquarter", ""))
                        if period_type == "quarterly"
                        else "FY"
                    )
                eps_estimates["number_of_analysts"] = num_estimates[0].get(
                    "dataitemvalue"
                )
                actual = seek_object["eps_normalized_actual"].get(str(i))
                if actual:
                    eps_estimates["normalized_actual"] = actual[0].get("dataitemvalue")
                gaap_actual = seek_object["eps_gaap_actual"].get(str(i))
                if gaap_actual:
                    eps_estimates["gaap_actual"] = gaap_actual[0].get("dataitemvalue")
                low = seek_object["eps_normalized_consensus_low"].get(str(i))
                if low:
                    eps_estimates["low_estimate"] = low[0].get("dataitemvalue")
                gaap_low = seek_object["eps_gaap_consensus_low"].get(str(i))
                if gaap_low:
                    eps_estimates["low_estimate_gaap"] = gaap_low[0].get(
                        "dataitemvalue"
                    )
                high = seek_object["eps_normalized_consensus_high"].get(str(i))
                if high:
                    eps_estimates["high_estimate"] = high[0].get("dataitemvalue")
                gaap_high = seek_object["eps_gaap_consensus_high"].get(str(i))
                if gaap_high:
                    eps_estimates["high_estimate_gaap"] = gaap_high[0].get(
                        "dataitemvalue"
                    )
                mean = seek_object["eps_normalized_consensus_mean"].get(str(i))
                if mean:
                    mean = mean[0].get("dataitemvalue")
                    eps_estimates["mean"] = mean
                gaap_mean = seek_object["eps_gaap_consensus_mean"].get(str(i))
                if gaap_mean:
                    eps_estimates["mean_gaap"] = gaap_mean[0].get("dataitemvalue")
                # Calculate the estimated growth percent.
                this = float(mean) if mean else None
                prev = None
                percent = None
                try:
                    prev = float(
                        seek_object["eps_normalized_actual"][str(i - 1)][0].get(
                            "dataitemvalue"
                        )
                    )
                except KeyError:
                    prev = float(
                        seek_object["eps_normalized_consensus_mean"][str(i - 1)][0].get(
                            "dataitemvalue"
                        )
                    )
                if this and prev:
                    percent = (this - prev) / prev
                eps_estimates["period_growth"] = percent
                results.append(SAForwardEpsEstimatesData.model_validate(eps_estimates))

        return results
