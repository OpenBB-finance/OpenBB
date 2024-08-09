"""FRED Mortgage Indices Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional, Union
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.mortgage_indices import (
    MortgageIndicesData,
    MortgageIndicesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fred.models.series import FredSeriesFetcher
from pydantic import Field, field_validator

MORTGAGE_ID_TO_TITLE = {
    "OBMMIC30YF": "30-Year Fixed Rate Conforming",
    "OBMMIC30YFNA": "30-Year Fixed Rate Conforming Non-Adjusted",
    "OBMMIJUMBO30YF": "30-Year Fixed Rate Jumbo",
    "OBMMIFHA30YF": "30-Year Fixed Rate FHA",
    "OBMMIVA30YF": "30-Year Fixed Rate Veterans Affairs",
    "OBMMIUSDA30YF": "30-Year Fixed Rate USDA",
    "OBMMIC15YF": "15-Year Fixed Rate Conforming",
    "OBMMIC30YFLVLE80FGE740": "30-Year Fixed Rate Conforming LTV <= 80 FICO >= 740",
    "OBMMIC30YFLVLE80FB720A739": "30-Year Fixed Rate Conforming LTV <= 80 FICO 720-739",
    "OBMMIC30YFLVLE80FB700A719": "30-Year Fixed Rate Conforming LTV <= 80 FICO 700-719",
    "OBMMIC30YFLVLE80FB680A699": "30-Year Fixed Rate Conforming LTV <= 80 FICO 680-699",
    "OBMMIC30YFLVLE80FLT680": "30-Year Fixed Rate Conforming LTV <= 80 FICO < 680",
    "OBMMIC30YFLVGT80FGE740": "30-Year Fixed Rate Conforming LTV > 80 FICO >= 740",
    "OBMMIC30YFLVGT80FB720A739": "30-Year Fixed Rate Conforming LTV > 80 FICO 720-739",
    "OBMMIC30YFLVGT80FB700A719": "30-Year Fixed Rate Conforming LTV > 80 FICO 700-719",
    "OBMMIC30YFLVGT80FB680A699": "30-Year Fixed Rate Conforming LTV > 80 FICO 680-699",
    "OBMMIC30YFLVGT80FLT680": "30-Year Fixed Rate Conforming LTV > 80 FICO < 680",
}

MORTGAGE_GROUPS = {
    "primary": [
        "OBMMIC30YF",
        "OBMMIC30YFNA",
        "OBMMIJUMBO30YF",
        "OBMMIFHA30YF",
        "OBMMIVA30YF",
        "OBMMIUSDA30YF",
        "OBMMIC15YF",
    ],
    "ltv_lte_80": [
        "OBMMIC30YFLVLE80FGE740",
        "OBMMIC30YFLVLE80FB720A739",
        "OBMMIC30YFLVLE80FB700A719",
        "OBMMIC30YFLVLE80FB680A699",
        "OBMMIC30YFLVLE80FLT680",
    ],
    "ltv_gt_80": [
        "OBMMIC30YFLVGT80FGE740",
        "OBMMIC30YFLVGT80FB720A739",
        "OBMMIC30YFLVGT80FB700A719",
        "OBMMIC30YFLVGT80FB680A699",
        "OBMMIC30YFLVGT80FLT680",
    ],
}

MORTGAGE_CHOICES_TO_ID = {
    "primary": ",".join(MORTGAGE_GROUPS["primary"]),
    "ltv_lte_80": ",".join(MORTGAGE_GROUPS["ltv_lte_80"]),
    "ltv_gt_80": ",".join(MORTGAGE_GROUPS["ltv_gt_80"]),
    "conforming_30y": "OBMMIC30YF",
    "conforming_30y_na": "OBMMIC30YFNA",
    "jumbo_30y": "OBMMIJUMBO30YF",
    "fha_30y": "OBMMIFHA30YF",
    "va_30y": "OBMMIVA30YF",
    "usda_30y": "OBMMIUSDA30YF",
    "conforming_15y": "OBMMIC15YF",
    "ltv_lte80_fico_ge740": "OBMMIC30YFLVLE80FGE740",
    "ltv_lte80_fico_a720b739": "OBMMIC30YFLVLE80FB720A739",
    "ltv_lte80_fico_a700b719": "OBMMIC30YFLVLE80FB700A719",
    "ltv_lte80_fico_a680b699": "OBMMIC30YFLVLE80FB680A699",
    "ltv_lte80_fico_lt680": "OBMMIC30YFLVLE80FLT680",
    "ltv_gt80_fico_ge740": "OBMMIC30YFLVGT80FGE740",
    "ltv_gt80_fico_a720b739": "OBMMIC30YFLVGT80FB720A739",
    "ltv_gt80_fico_a700b719": "OBMMIC30YFLVGT80FB700A719",
    "ltv_gt80_fico_a680b699": "OBMMIC30YFLVGT80FB680A699",
    "ltv_gt80_fico_lt680": "OBMMIC30YFLVGT80FLT680",
}

MortgageChoices = Literal[
    "primary",
    "ltv_lte_80",
    "ltv_gt_80",
    "conforming_30y",
    "conforming_30y_na",
    "jumbo_30y",
    "fha_30y",
    "va_30y",
    "usda_30y",
    "conforming_15y",
    "ltv_lte80_fico_ge740",
    "ltv_lte80_fico_a720b739",
    "ltv_lte80_fico_a700b719",
    "ltv_lte80_fico_a680b699",
    "ltv_lte80_fico_lt680",
    "ltv_gt80_fico_ge740",
    "ltv_gt80_fico_a720b739",
    "ltv_gt80_fico_a700b719",
    "ltv_gt80_fico_a680b699",
    "ltv_gt80_fico_lt680",
]


class FredMortgageIndicesQueryParams(MortgageIndicesQueryParams):
    """FRED Mortgage Indices Query."""

    __json_schema_extra__ = {
        "index": {
            "multiple_items_allowed": True,
            "choices": list(MORTGAGE_CHOICES_TO_ID),
        }
    }

    index: Union[MortgageChoices, str] = Field(
        default="primary",
        description="The specific index, or index group, to query. Default is the 'primary' group.",
    )
    frequency: Union[
        None,
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
        ],
    ] = Field(
        default=None,
        description="""
        Frequency aggregation to convert daily data to lower frequency.
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
    aggregation_method: Literal["avg", "sum", "eop"] = Field(
        default="avg",
        description="""
        A key that indicates the aggregation method used for frequency aggregation.
        This parameter has no affect if the frequency parameter is not set, default is 'avg'.
            avg = Average
            sum = Sum
            eop = End of Period
        """,
        json_schema_extra={"choices": ["avg", "sum", "eop"]},
    )
    transform: Union[
        None, Literal["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"]
    ] = Field(
        default=None,
        description="""
        Transformation type
            None = No transformation
            chg = Change
            ch1 = Change from Year Ago
            pch = Percent Change
            pc1 = Percent Change from Year Ago
            pca = Compounded Annual Rate of Change
            cch = Continuously Compounded Rate of Change
            cca = Continuously Compounded Annual Rate of Change
            log = Natural Log
        """,
        json_schema_extra={
            "choices": ["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"]
        },
    )

    @field_validator("index", mode="before", check_fields=False)
    @classmethod
    def validate_index(cls, v):
        """Validate index."""
        indices = v.split(",")
        new_indices: List = []
        for index in indices:
            if index in MORTGAGE_CHOICES_TO_ID:
                new_indices.append(index)
            else:
                warn(f"Invalid index '{index}' will be ignored.")
        if not new_indices:
            raise OpenBBError(
                f"No valid indices found. Must be any of: {list(MORTGAGE_CHOICES_TO_ID.keys())}"
            )
        return ",".join(new_indices)


class FredMortgageIndicesData(MortgageIndicesData):
    """FRED Mortgage Indices Data."""


class FredMortgageIndicesFetcher(
    Fetcher[
        FredMortgageIndicesQueryParams,
        List[FredMortgageIndicesData],
    ]
):
    """FRED Mortgage Indices Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredMortgageIndicesQueryParams:
        """Transform query."""
        return FredMortgageIndicesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredMortgageIndicesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract data."""
        indices = query.index.split(",")
        ids = [MORTGAGE_CHOICES_TO_ID[index] for index in indices]
        try:
            response = await FredSeriesFetcher.fetch_data(
                dict(
                    symbol=",".join(ids),
                    start_date=query.start_date,
                    end_date=query.end_date,
                    transform=query.transform,
                    frequency=query.frequency,
                    aggregation_method=query.aggregation_method,
                ),
                credentials,
            )
        except Exception as e:
            raise e from e

        return {
            "metadata": response.metadata,
            "data": [d.model_dump() for d in response.result],
        }

    @staticmethod
    def transform_data(
        query: FredMortgageIndicesQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> AnnotatedResult[List[FredMortgageIndicesData]]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from pandas import Categorical, DataFrame

        if not data.get("data"):
            raise EmptyDataError("The request was returned empty.")
        df = DataFrame.from_records(data["data"])
        metadata = data.get("metadata", {})
        # Flatten the data.
        df = (
            df.melt(id_vars="date", var_name="symbol", value_name="value")
            .query("value.notnull()")
            .rename(columns={"value": "rate"})
        )
        df["name"] = df.symbol.map(MORTGAGE_ID_TO_TITLE)
        # Normalize the percent values.
        df["rate"] = df["rate"] / 100
        df = df.fillna("N/A").replace("N/A", None)
        df["name"] = Categorical(
            df["name"],
            categories=[
                d
                for d in list(MORTGAGE_ID_TO_TITLE.values())
                if d in df["name"].unique()
            ],
            ordered=True,
        )
        df.sort_values(["date", "name"], inplace=True)
        records = df.to_dict(orient="records")

        return AnnotatedResult(
            result=[FredMortgageIndicesData.model_validate(r) for r in records],
            metadata=metadata,
        )
