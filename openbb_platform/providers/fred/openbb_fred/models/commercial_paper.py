"""FRED Commercial Paper Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.commercial_paper import (
    CommercialPaperData,
    CommercialPaperParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, create_model

from openbb_fred.models.series import FredSeriesFetcher
from openbb_fred.utils.api import unwrap_series
from openbb_fred.utils.columns import TIME_COLUMN, series_field
from openbb_fred.utils.query import UseCacheQueryParams

CP_SERIES_IDS = {
    "RIFSPPAAAD01NB": {
        "maturity": "overnight",
        "asset": "asset_backed",
        "title": "Overnight AA Asset-Backed Commercial Paper Interest Rate",
    },
    "RIFSPPAAAD07NB": {
        "maturity": "day_7",
        "asset": "asset_backed",
        "title": "7-Day AA Asset-Backed Commercial Paper Interest Rate",
    },
    "RIFSPPAAAD15NB": {
        "maturity": "day_15",
        "asset": "asset_backed",
        "title": "15-Day AA Asset-Backed Commercial Paper Interest Rate",
    },
    "RIFSPPAAAD30NB": {
        "maturity": "day_30",
        "asset": "asset_backed",
        "title": "30-Day AA Asset-Backed Commercial Paper Interest Rate",
    },
    "RIFSPPAAAD60NB": {
        "maturity": "day_60",
        "asset": "asset_backed",
        "title": "60-Day AA Asset-Backed Commercial Paper Interest Rate",
    },
    "RIFSPPAAAD90NB": {
        "maturity": "day_90",
        "asset": "asset_backed",
        "title": "90-Day AA Asset-Backed Commercial Paper Interest Rate",
    },
    "RIFSPPFAAD01NB": {
        "maturity": "overnight",
        "asset": "financial",
        "title": "Overnight AA Financial Commercial Paper Interest Rate",
    },
    "RIFSPPFAAD07NB": {
        "maturity": "day_7",
        "asset": "financial",
        "title": "7-Day AA Financial Commercial Paper Interest Rate",
    },
    "RIFSPPFAAD15NB": {
        "maturity": "day_15",
        "asset": "financial",
        "title": "15-Day AA Financial Commercial Paper Interest Rate",
    },
    "RIFSPPFAAD30NB": {
        "maturity": "day_30",
        "asset": "financial",
        "title": "30-Day AA Financial Commercial Paper Interest Rate",
    },
    "RIFSPPFAAD60NB": {
        "maturity": "day_60",
        "asset": "financial",
        "title": "60-Day AA Financial Commercial Paper Interest Rate",
    },
    "RIFSPPFAAD90NB": {
        "maturity": "day_90",
        "asset": "financial",
        "title": "90-Day AA Financial Commercial Paper Interest Rate",
    },
    "RIFSPPNAAD01NB": {
        "maturity": "overnight",
        "asset": "nonfinancial",
        "title": "Overnight AA Nonfinancial Commercial Paper Interest Rate",
    },
    "RIFSPPNAAD07NB": {
        "maturity": "day_7",
        "asset": "nonfinancial",
        "title": "7-Day AA Nonfinancial Commercial Paper Interest Rate",
    },
    "RIFSPPNAAD15NB": {
        "maturity": "day_15",
        "asset": "nonfinancial",
        "title": "15-Day AA Nonfinancial Commercial Paper Interest Rate",
    },
    "RIFSPPNAAD30NB": {
        "maturity": "day_30",
        "asset": "nonfinancial",
        "title": "30-Day AA Nonfinancial Commercial Paper Interest Rate",
    },
    "RIFSPPNAAD60NB": {
        "maturity": "day_60",
        "asset": "nonfinancial",
        "title": "60-Day AA Nonfinancial Commercial Paper Interest Rate",
    },
    "RIFSPPNAAD90NB": {
        "maturity": "day_90",
        "asset": "nonfinancial",
        "title": "90-Day AA Nonfinancial Commercial Paper Interest Rate",
    },
    "RIFSPPNA2P2D01NB": {
        "maturity": "overnight",
        "asset": "a2p2",
        "title": "Overnight A2/P2 Nonfinancial Commercial Paper Interest Rate",
    },
    "RIFSPPNA2P2D07NB": {
        "maturity": "day_7",
        "asset": "a2p2",
        "title": "7-Day A2/P2 Nonfinancial Commercial Paper Interest Rate",
    },
    "RIFSPPNA2P2D15NB": {
        "maturity": "day_15",
        "asset": "a2p2",
        "title": "15-Day A2/P2 Nonfinancial Commercial Paper Interest Rate",
    },
    "RIFSPPNA2P2D30NB": {
        "maturity": "day_30",
        "asset": "a2p2",
        "title": "30-Day A2/P2 Nonfinancial Commercial Paper Interest Rate",
    },
    "RIFSPPNA2P2D60NB": {
        "maturity": "day_60",
        "asset": "a2p2",
        "title": "60-Day A2/P2 Nonfinancial Commercial Paper Interest Rate",
    },
    "RIFSPPNA2P2D90NB": {
        "maturity": "day_90",
        "asset": "a2p2",
        "title": "90-Day A2/P2 Nonfinancial Commercial Paper Interest Rate",
    },
}
ALL_IDS = list(CP_SERIES_IDS)


class FREDCommercialPaperParams(UseCacheQueryParams, CommercialPaperParams):
    """FRED Commercial Paper Query."""

    __json_schema_extra__ = {
        "maturity": {
            "multiple_items_allowed": True,
            "choices": ["all", "overnight", "7d", "15d", "30d", "60d", "90d"],
        },
        "category": {
            "multiple_items_allowed": True,
            "choices": ["all", "asset_backed", "financial", "nonfinancial", "a2p2"],
        },
    }

    maturity: str | Literal["all", "overnight", "7d", "15d", "30d", "60d", "90d"] = (
        Field(
            default="all",
            description="A target maturity.",
        )
    )
    category: (
        str | Literal["all", "asset_backed", "financial", "nonfinancial", "a2p2"]
    ) = Field(
        default="all",
        description="The category of asset.",
    )
    frequency: (
        None
        | Literal[
            "a",
            "q",
            "m",
            "w",
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
    ) = Field(
        default=None,
        description="""
        Frequency aggregation to convert daily data to lower frequency.
            a = Annual
            q = Quarterly
            m = Monthly
            w = Weekly
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
    aggregation_method: None | Literal["avg", "sum", "eop"] = Field(
        default=None,
        description="""
        A key that indicates the aggregation method used for frequency aggregation.
            avg = Average
            sum = Sum
            eop = End of Period
        """,
        json_schema_extra={"choices": ["avg", "sum", "eop"]},
    )
    transform: (
        None | Literal["chg", "ch1", "pch", "pc1", "pca", "cch", "cca", "log"]
    ) = Field(
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


CP_ID_TO_COLUMN = {
    series_id: f"{spec['asset']}_{spec['maturity']}"
    for series_id, spec in CP_SERIES_IDS.items()
}


def _commercial_paper_fields() -> dict:
    """Declare one column for every maturity and category published."""
    return {
        CP_ID_TO_COLUMN[series_id]: series_field(spec["title"])
        for series_id, spec in CP_SERIES_IDS.items()
    }


FREDCommercialPaperData = create_model(
    "FREDCommercialPaperData",
    __base__=CommercialPaperData,
    __doc__="FRED Commercial Paper Data.",
    date=(
        dateType,
        Field(
            description=DATA_DESCRIPTIONS.get("date", ""),
            json_schema_extra=TIME_COLUMN,
        ),
    ),
    **_commercial_paper_fields(),
)


class FREDCommercialPaperFetcher(
    Fetcher[
        FREDCommercialPaperParams,
        list[FREDCommercialPaperData],  # ty: ignore[invalid-type-form]
    ]
):
    """FRED Commercial Paper Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FREDCommercialPaperParams:
        """Transform query."""
        return FREDCommercialPaperParams(**params)

    @staticmethod
    async def aextract_data(
        query: FREDCommercialPaperParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Extract data."""
        ids: list[str] = []
        if query.maturity == "all" and query.category == "all":
            ids = ALL_IDS
        else:
            MAT_DICT = {
                "overnight": "01",
                "7d": "07",
                "15d": "15",
                "30d": "30",
                "60d": "60",
                "90d": "90",
            }
            CAT_DICT = {
                "asset_backed": "AAAD",
                "financial": "FAAD",
                "nonfinancial": "NAAD",
                "a2p2": "NA2P2D",
            }
            maturities = query.maturity.split(",")
            categories = query.category.split(",")
            if "all" in categories:
                categories = list(CAT_DICT)
            if "all" in maturities:
                maturities = list(MAT_DICT)
            for cat in categories:
                for mat in maturities:
                    ids.append(f"RIFSPP{CAT_DICT.get(cat)}{MAT_DICT.get(mat)}NB")
        try:
            response = await FredSeriesFetcher.fetch_data(
                dict(
                    symbol=",".join(ids),
                    start_date=query.start_date if query.start_date else "2019-01-01",
                    end_date=query.end_date,
                    frequency=query.frequency,
                    aggregation_method=query.aggregation_method,
                    transform=query.transform,
                    use_cache=query.use_cache,
                ),
                credentials,
            )
        except Exception as e:
            raise e from e

        rows, metadata = unwrap_series(response)

        return {
            "metadata": metadata,
            "data": [d.model_dump() for d in rows],
        }

    @staticmethod
    def transform_data(
        query: FREDCommercialPaperParams,
        data: dict,
        **kwargs: Any,
    ) -> AnnotatedResult[list[FREDCommercialPaperData]]:  # ty: ignore[invalid-type-form]
        """Transform data."""
        from numpy import nan
        from pandas import DataFrame

        if not data.get("data"):
            raise EmptyDataError("The request was returned empty.")
        df = DataFrame(data["data"])
        metadata = data.get("metadata", {})
        published = [c for c in CP_ID_TO_COLUMN if c in df.columns]
        df = df[["date", *published]].rename(columns=CP_ID_TO_COLUMN)
        df = df.replace({nan: None}).sort_values("date")
        records = df.to_dict(orient="records")

        return AnnotatedResult(
            result=[FREDCommercialPaperData.model_validate(d) for d in records],
            metadata=metadata,
        )
