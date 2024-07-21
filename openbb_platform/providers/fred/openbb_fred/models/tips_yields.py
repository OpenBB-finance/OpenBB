"""FRED TIPS Yields Model."""

# pylint: disable=unused-argument,too-many-locals

from typing import Any, Dict, List, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.tips_yields import (
    TipsYieldsData,
    TipsYieldsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FredTipsYieldsQueryParams(TipsYieldsQueryParams):
    """FRED TIPS Yields Query."""

    maturity: Optional[Literal[5, 10, 20, 30]] = Field(
        default=None,
        description="The maturity of the security in years - 5, 10, 20, 30 - defaults to all."
        + " Note that the maturity is the tenor of the security, not the time to maturity.",
        json_schema_extra={"choices": [5, 10, 20, 30]},
    )
    frequency: Optional[
        Literal[
            "a",
            "q",
            "m",
            "w",
            "d",
            "wef",
            "weth",
            "wew",
            "wetu",
            "wem",
            "wesu",
            "wesa",
            "bwew",
            "bwem",
        ]
    ] = Field(
        default=None,
        description="""Frequency aggregation to convert high frequency data to lower frequency.
            None = No change
            a = Annual
            q = Quarterly
            m = Monthly
            w = Weekly
            d = Daily
            wef = Weekly, Ending Friday
            weth = Weekly, Ending Thursday
            wew = Weekly, Ending Wednesday
            wetu = Weekly, Ending Tuesday
            wem = Weekly, Ending Monday
            wesu = Weekly, Ending Sunday
            wesa = Weekly, Ending Saturday
            bwew = Biweekly, Ending Wednesday
            bwem = Biweekly, Ending Monday
        """,
        json_schema_extra={
            "choices": [
                "a",
                "q",
                "m",
                "w",
                "d",
                "wef",
                "weth",
                "wew",
                "wetu",
                "wem",
                "wesu",
                "wesa",
                "bwew",
                "bwem",
            ]
        },
    )
    aggregation_method: Optional[Literal["avg", "sum", "eop"]] = Field(
        default=None,
        description="""A key that indicates the aggregation method used for frequency aggregation.
            avg = Average
            sum = Sum
            eop = End of Period
        """,
        json_schema_extra={"choices": ["avg", "sum", "eop"]},
    )
    transform: Optional[Literal["chg", "ch1", "pch", "pc1", "pca", "cch", "cca"]] = (
        Field(
            default=None,
            description="""Transformation type
            None = No transformation
            chg = Change
            ch1 = Change from Year Ago
            pch = Percent Change
            pc1 = Percent Change from Year Ago
            pca = Compounded Annual Rate of Change
            cch = Continuously Compounded Rate of Change
            cca = Continuously Compounded Annual Rate of Change
        """,
            json_schema_extra={
                "choices": ["chg", "ch1", "pch", "pc1", "pca", "cch", "cca"]
            },
        )
    )


class FredTipsYieldsData(TipsYieldsData):
    """FRED TIPS Yields Data."""


class FredTipsYieldsFetcher(
    Fetcher[
        FredTipsYieldsQueryParams,
        List[FredTipsYieldsData],
    ]
):
    """FRED TIPS Yields Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredTipsYieldsQueryParams:
        """Transform the query."""
        return FredTipsYieldsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredTipsYieldsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract the data."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.command_runner import CommandRunner
        from pandas import to_datetime

        api_key = (  # pylint: disable=unused-variable  # noqa: F841
            credentials.get("fred_api_key") if credentials else ""
        )

        # We get the series IDs because they will change over time.
        async def get_tips_series():
            """Get series IDs for the TIPS."""
            res = await CommandRunner().run(
                "/economy/fred_search",
                provider_choices={
                    "provider": "fred",
                },
                standard_params={},
                extra_params={
                    "release_id": 72,
                },
            )  # type: ignore
            df = (
                res.to_df()  # type: ignore
                .query("not title.str.contains('DISCONTINUED')")
                .set_index("series_id")
            )
            df.loc[:, "due"] = df.title.apply(
                lambda x: x.split("Due ")[-1].strip()
            ).apply(to_datetime)
            df = df[["due", "observation_start", "observation_end", "title"]]
            return df.sort_values(by="due").reset_index()  # type: ignore

        try:
            ids_df = await get_tips_series()
            ids = ids_df.series_id.to_list()
        except Exception as e:
            raise OpenBBError(e) from e

        # If we are looking for a specific tenor, the request will be smaller.
        if query.maturity:
            ids = [i for i in ids if str(i[3]) == (f"{str(query.maturity)[0]}")]

        # We split the due date from the title so that we can format it as a datetime.date object.
        due_map = ids_df.set_index("series_id")["due"].dt.date.to_dict()
        # We make a seriesID-title map for later.
        title_map = (
            ids_df.set_index("series_id")["title"]
            .str.replace("Treasury Inflation-Indexed", "TIPS")
            .str.replace("  ", " ")
            .str.strip()
            .to_dict()
        )

        try:
            res = await CommandRunner().run(
                "/economy/fred_series",
                provider_choices={
                    "provider": "fred",
                },
                standard_params={
                    "symbol": ",".join(ids),
                    "start_date": query.start_date,
                    "end_date": query.end_date,
                },
                extra_params={
                    "frequency": query.frequency,
                    "aggregation_method": query.aggregation_method,
                    "transform": query.transform,
                },
            )  # type: ignore
            df = res.to_df(index=None)  # type: ignore
            meta = res.extra["results_metadata"]
        except Exception as e:
            raise OpenBBError(e) from e

        for k, v in title_map.items():
            if k in meta:
                meta[k]["title"] = v

        # We flatten the data and format the output with the metadata.
        df = (
            df.melt(
                id_vars="date",
                value_vars=[d for d in df.columns if d != "date"],
                var_name="symbol",
            )
            .dropna()
            .sort_values(by="date")
        )
        df = df.reset_index(drop=True)
        df["due"] = df.symbol.map(due_map)
        df["name"] = df.symbol.map(title_map)
        df["value"] = df["value"] / 100
        df = df[["date", "due", "symbol", "name", "value"]]
        df = df.sort_values(by=["date", "due"])  # type: ignore
        records = df.to_dict(orient="records")
        output = {
            "records": records,
            "meta": meta,
        }

        return output

    @staticmethod
    def transform_data(
        query: FredTipsYieldsQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> AnnotatedResult[List[FredTipsYieldsData]]:
        """Transform the data."""
        results = data.get("records", [])
        meta = data.get("meta", {})
        if not results:
            raise EmptyDataError(
                "There was an error with the request and was returned empty."
            )

        return AnnotatedResult(
            result=[FredTipsYieldsData.model_validate(r) for r in results],
            metadata=meta,
        )
