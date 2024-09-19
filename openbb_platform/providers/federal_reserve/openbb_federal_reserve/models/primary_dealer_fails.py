"""Federal Reserve Primary Dealer Fails Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.primary_dealer_fails import (
    PrimaryDealerFailsData,
    PrimaryDealerFailsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_federal_reserve.utils.primary_dealer_statistics import FAILS_SERIES_TO_TITLE
from pydantic import Field


class FederalReservePrimaryDealerFailsQueryParams(PrimaryDealerFailsQueryParams):
    """Federal Reserve Primary Dealer Fails Query Params."""

    __json_schema_extra__ = {
        "asset_class": {
            "multiple_items_allowed": False,
            "choices": ["all", "treasuries", "tips", "agency", "mbs", "corporate"],
        },
        "unit": {
            "multiple_items_allowed": False,
            "choices": ["value", "percent"],
        },
    }

    asset_class: Literal["all", "treasuries", "tips", "agency", "mbs", "corporate"] = (
        Field(
            default="all",
            description="Asset class to return, default is 'all'.",
        )
    )
    unit: Literal["value", "percent"] = Field(
        default="value",
        description="Unit of the data returned to the 'value' field."
        + " Default is 'value', which represents millions of USD."
        + " 'percent' returns data as the percentage of the total"
        + " fails-to-receive and fails-to-deliver, by asset class.",
    )


class FederalReservePrimaryDealerFailsData(PrimaryDealerFailsData):
    """Federal Reserve Primary Dealer Fails Data."""

    title: str = Field(description="Title of the series' symbol.")
    value: Union[int, float] = Field(
        description="Value of the data returned, in millions of USD if the `unit`"
        + " parameter is 'value' else a normalized percent."
    )


class FederalReservePrimaryDealerFailsFetcher(
    Fetcher[
        FederalReservePrimaryDealerFailsQueryParams,
        List[FederalReservePrimaryDealerFailsData],
    ]
):
    """Federal Reserve Primary Dealer Fails Fetcher."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FederalReservePrimaryDealerFailsQueryParams:
        """Transform the query parameters."""
        return FederalReservePrimaryDealerFailsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FederalReservePrimaryDealerFailsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Federal Reserve endpoint."""
        # pylint: disable=import-outside-toplevel
        from datetime import datetime  # noqa
        from openbb_core.provider.utils.helpers import amake_request

        url = (
            "https://markets.newyorkfed.org/api/pd/get/"
            + "PDFTD-CS_PDFTR-CS_PDFTD-FGEM_PDFTR-FGEM_PDFTD-FGM_PDFTR-FGM_PDFTD-OM_"
            + "PDFTR-OM_PDFTD-UST_PDFTR-UST_PDFTD-USTET_PDFTR-USTET.json"
        )
        try:

            response = await amake_request(url, **kwargs)
            data = response.get("pd", {}).get("timeseries", [])  # type: ignore
            if query.start_date and query.start_date < datetime(2013, 4, 1).date():
                # The data is broken into different series and the structure of the data is different over time.
                if query.start_date < datetime(2001, 7, 1).date():
                    url2 = (
                        "https://markets.newyorkfed.org/api/pd/get/SBP2001/timeseries/PDFASUFDA_PDFASUFRA"
                        + "_PDFASFAFDA_PDFASFAFRA_PDFASMBFDA_PDFASMBFRA.json"
                    )
                    response = await amake_request(url2, **kwargs)
                    data += response.get("pd", {}).get("timeseries", [])  # type: ignore
                url = (
                    "https://markets.newyorkfed.org/api/pd/get/SBP2013/timeseries/"
                    + "PDFASCFRA_PDFASCFDA_PDFASFAFRA_PDFASFAFDA_PDFASMBFRA_PDFASMBFDA_PDFASUFRA_PDFASUFDA.json"
                )
                response = await amake_request(url, **kwargs)
                data += response.get("pd", {}).get("timeseries", [])  # type: ignore
            return data
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(
                "Failed to fetch data from the Federal Reserve API."
            ) from e

    @staticmethod
    def transform_data(
        query: FederalReservePrimaryDealerFailsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FederalReservePrimaryDealerFailsData]:
        """Transform the raw data into the standard format."""
        # pylint: disable=import-outside-toplevel
        from pandas import NA, DataFrame, concat, to_datetime

        if not data:
            raise EmptyDataError("No data returned from the Federal Reserve API.")

        df = DataFrame(data)
        df.loc[:, "title"] = df.keyid.map(FAILS_SERIES_TO_TITLE)
        df.value = df.value.astype(int)
        new_df = df.pivot(index="asofdate", columns="title", values="value").copy()
        new_data = new_df.copy()
        combined_df = DataFrame()

        for target in ["FTD", "FTR"]:
            total_col = target + " Total"
            new_data = new_df[[d for d in new_df.columns if target in d]].copy()
            new_data.loc[:, total_col] = new_data.sum(axis=1)

            if query.unit == "percent":
                new_data = new_data.div(new_data[total_col], axis=0)

            combined_df = (
                new_data.copy()
                if combined_df.empty
                else concat([combined_df, new_data], axis=1)
            )
        new_data = combined_df

        if query.asset_class == "agency":
            new_data = new_data[[d for d in new_data.columns if "Ex-MBS" in d]]
        if query.asset_class == "mbs":
            new_data = new_data[
                [d for d in new_data.columns if "MBS" in d and "Ex-MBS" not in d]
            ]
        if query.asset_class == "treasuries":
            new_data = new_data[
                [d for d in new_data.columns if "Treasury Securities (Ex-TIPS)" in d]
            ]
        if query.asset_class == "tips":
            new_data = new_data[
                [d for d in new_data.columns if "TIPS" in d and "Ex-TIPS" not in d]
            ]
        if query.asset_class == "corporate":
            new_data = new_data[[d for d in new_data.columns if "Corporate" in d]]

        new_data = new_data.T.unstack().reset_index()
        new_data.columns = ["date", "title", "value"]
        new_data.loc[:, "symbol"] = new_data.title.map(
            {v: k for k, v in FAILS_SERIES_TO_TITLE.items()}
        ).replace({NA: "--"})
        new_data = new_data.dropna()

        if query.unit == "value":
            new_data.value = new_data.value.astype(int)

        new_data.date = to_datetime(new_data.date).dt.date

        if query.start_date:
            new_data = new_data[new_data.date >= query.start_date]

        if query.end_date:
            new_data = new_data[new_data.date <= query.end_date]

        return [
            FederalReservePrimaryDealerFailsData.model_validate(r)
            for r in new_data.dropna().to_dict(orient="records")
        ]
