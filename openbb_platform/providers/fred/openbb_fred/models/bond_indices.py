"""FRED Bond Indices Model."""

# pylint: disable=unused-argument,too-many-statements,too-many-branches

from typing import Any, Dict, List, Literal, Optional, Union
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.bond_indices import (
    BondIndicesData,
    BondIndicesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fred.models.series import FredSeriesFetcher
from pydantic import Field, PrivateAttr

BAML_CATEGORIES = {
    "high_yield": {
        "us": {
            "total_return": "BAMLHYH0A0HYM2TRIV",
            "yield": "BAMLH0A0HYM2EY",
            "oas": "BAMLH0A0HYM2",
            "yield_to_worst": "BAMLH0A0HYM2SYTW",
        },
        "europe": {
            "total_return": "BAMLHE00EHYITRIV",
            "yield": "BAMLHE00EHYIEY",
            "oas": "BAMLHE00EHYIOAS",
            "yield_to_worst": "BAMLHE00EHYISYTW",
        },
        "emerging": {
            "total_return": "BAMLEMHBHYCRPITRIV",
            "yield": "BAMLEMHBHYCRPIEY",
            "oas": "BAMLEMHBHYCRPIOAS",
            "yield_to_worst": "BAMLEMHBHYCRPISYTW",
        },
    },
    "us": {
        "corporate": {
            "total_return": "BAMLCC0A0CMTRIV",
            "yield": "BAMLC0A0CMEY",
            "oas": "BAMLC0A0CM",
            "yield_to_worst": "BAMLC0A0CMSYTW",
        },
        "seasoned_corporate": {
            "total_return": "",
            "yield": "DAAA,AAA10Y,AAAFF,DBAA,BAA10Y,BAAFF",
            "oas": "",
            "yield_to_worst": "",
        },
        "high_yield": {
            "total_return": "BAMLHYH0A0HYM2TRIV",
            "yield": "BAMLH0A0HYM2EY",
            "oas": "BAMLH0A0HYM2",
            "yield_to_worst": "BAMLH0A0HYM2SYTW",
        },
        "yield_curve": {
            "year1_year3": {
                "total_return": "BAMLCC1A013YTRIV",
                "yield": "BAMLC1A0C13YEY",
                "oas": "BAMLC1A0C13Y",
                "yield_to_worst": "BAMLC1A0C13YSYTW",
            },
            "year3_year5": {
                "total_return": "BAMLCC2A035YTRIV",
                "yield": "BAMLC2A0C35YEY",
                "oas": "BAMLC2A0C35Y",
                "yield_to_worst": "BAMLC2A0C35YSYTW",
            },
            "year5_year7": {
                "total_return": "BAMLCC3A057YTRIV",
                "yield": "BAMLC3A0C57YEY",
                "oas": "BAMLC3A0C57Y",
                "yield_to_worst": "BAMLC3A0C57YSYTW",
            },
            "year7_year10": {
                "total_return": "BAMLCC4A0710YTRIV",
                "yield": "BAMLC4A0C710YEY",
                "oas": "BAMLC4A0C710Y",
                "yield_to_worst": "BAMLC4A0C710YSYTW",
            },
            "year10_year15": {
                "total_return": "BAMLCC7A01015YTRIV",
                "yield": "BAMLC7A0C1015YEY",
                "oas": "BAMLC7A0C1015Y",
                "yield_to_worst": "BAMLC7A0C1015YSYTW",
            },
            "year15+": {
                "total_return": "BAMLCC8A015PYTRIV",
                "yield": "BAMLC8A0C15PYEY",
                "oas": "BAMLC8A0C15PY",
                "yield_to_worst": "BAMLC8A0C15PYSYTW",
            },
        },
        "aaa": {
            "total_return": "BAMLCC0A1AAATRIV",
            "yield": "BAMLC0A1CAAAEY",
            "oas": "BAMLC0A1CAAA",
            "yield_to_worst": "BAMLC0A1CAAASYTW",
        },
        "aa": {
            "total_return": "BAMLCC0A2AATRIV",
            "yield": "BAMLC0A2CAAEY",
            "oas": "BAMLC0A2CAA",
            "yield_to_worst": "BAMLC0A2CAASYTW",
        },
        "a": {
            "total_return": "BAMLCC0A3ATRIV",
            "yield": "BAMLC0A3CAEY",
            "oas": "BAMLC0A3CA",
            "yield_to_worst": "BAMLC0A3CASYTW",
        },
        "bbb": {
            "total_return": "BAMLCC0A4BBBTRIV",
            "yield": "BAMLC0A4CBBBEY",
            "oas": "BAMLC0A4CBBB",
            "yield_to_worst": "BAMLC0A4CBBBSYTW",
        },
        "bb": {
            "total_return": "BAMLHYH0A1BBTRIV",
            "yield": "BAMLH0A1HYBBEY",
            "oas": "BAMLH0A1HYBB",
            "yield_to_worst": "BAMLH0A1HYBBSYTW",
        },
        "b": {
            "total_return": "BAMLHYH0A2BTRIV",
            "yield": "BAMLH0A2HYBEY",
            "oas": "BAMLH0A2HYB",
            "yield_to_worst": "BAMLH0A2HYBSYTW",
        },
        "ccc": {
            "total_return": "BAMLHYH0A3CMTRIV",
            "yield": "BAMLH0A3HYCEY",
            "oas": "BAMLH0A3HYCC",
            "yield_to_worst": "BAMLH0A3HYCCSYTW",
        },
    },
    "emerging_markets": {
        "corporate": {
            "total_return": "BAMLEMCBPITRIV",
            "yield": "BAMLEMCBPIEY",
            "yield_to_worst": "BAMLEMCBPISYTW",
            "oas": "BAMLEMCBPIOAS",
        },
        "liquid_corporate": {
            "total_return": "BAMLEMCLLCRPIUSTRIV",
            "yield": "BAMLEMCLLCRPIUSEY",
            "yield_to_worst": "BAMLEMCLLCRPIUSSYTW",
            "oas": "BAMLEMCLLCRPIUSOAS",
        },
        "crossover": {
            "total_return": "BAMLEM5BCOCRPITRIV",
            "yield": "BAMLEM5BCOCRPIEY",
            "oas": "BAMLEM5BCOCRPIOAS",
            "yield_to_worst": "BAMLEM5BCOCRPISYTW",
        },
        "public_sector": {
            "total_return": "BAMLEMPUPUBSLCRPIUSTRIV",
            "yield": "BAMLEMPUPUBSLCRPIUSEY",
            "oas": "BAMLEMPUPUBSLCRPIUSOAS",
            "yield_to_worst": "BAMLEMPUPUBSLCRPIUSSYTW",
        },
        "private_sector": {
            "total_return": "BAMLEMFSFCRPITRIV",
            "yield": "BAMLEMFSFCRPIEY",
            "oas": "BAMLEMFSFCRPIOAS",
            "yield_to_worst": "BAMLEMFSFCRPISYTW",
        },
        "non_financial": {
            "total_return": "BAMLEMNFNFLCRPIUSTRIV",
            "yield": "BAMLEMNFNFLCRPIUSEY",
            "oas": "BAMLEMNFNFLCRPIUSOAS",
            "yield_to_worst": "BAMLEMNFNFLCRPIUSSYTW",
        },
        "high_grade": {
            "total_return": "BAMLEMIBHGCRPITRIV",
            "yield": "BAMLEMIBHGCRPIEY",
            "oas": "BAMLEMIBHGCRPIOAS",
            "yield_to_worst": "BAMLEMIBHGCRPISYTW",
        },
        "high_yield": {
            "total_return": "BAMLEMHBHYCRPITRIV",
            "yield": "BAMLEMHBHYCRPIEY",
            "oas": "BAMLEMHBHYCRPIOAS",
            "yield_to_worst": "BAMLEMHBHYCRPISYTW",
        },
        "liquid_emea": {
            "total_return": "BAMLEMELLCRPIEMEAUSTRIV",
            "yield": "BAMLEMELLCRPIEMEAUSEY",
            "oas": "BAMLEMELLCRPIEMEAUSOAS",
            "yield_to_worst": "BAMLEMELLCRPIEMEAUSSYTW",
        },
        "emea": {
            "total_return": "BAMLEMRECRPIEMEATRIV",
            "yield": "BAMLEMRECRPIEMEAEY",
            "oas": "BAMLEMRECRPIEMEAOAS",
            "yield_to_worst": "BAMLEMRECRPIEMEASYTW",
        },
        "liquid_asia": {
            "total_return": "BAMLEMALLCRPIASIAUSTRIV",
            "yield": "BAMLEMALLCRPIASIAUSEY",
            "oas": "BAMLEMALLCRPIASIAUSOAS",
            "yield_to_worst": "BAMLEMALLCRPIASIAUSSYTW",
        },
        "asia": {
            "total_return": "BAMLEMRACRPIASIATRIV",
            "yield": "BAMLEMRACRPIASIAEY",
            "oas": "BAMLEMRACRPIASIAOAS",
            "yield_to_worst": "BAMLEMRACRPIASIASYTW",
        },
        "liquid_latam": {
            "total_return": "BAMLEMLLLCRPILAUSTRIV",
            "yield": "BAMLEMLLLCRPILAUSEY",
            "oas": "BAMLEMLLLCRPILAUSOAS",
            "yield_to_worst": "BAMLEMLLLCRPILAUSSYTW",
        },
        "latam": {
            "total_return": "BAMLEMRLCRPILATRIV",
            "yield": "BAMLEMRLCRPILAEY",
            "oas": "BAMLEMRLCRPILAOAS",
            "yield_to_worst": "BAMLEMRLCRPILASYTW",
        },
        "liquid_aaa": {
            "total_return": "BAMLEM1RAAA2ALCRPIUSTRIV",
            "yield": "BAMLEM1RAAA2ALCRPIUSEY",
            "oas": "BAMLEM1RAAA2ALCRPIUSOAS",
            "yield_to_worst": "BAMLEM1RAAA2ALCRPIUSSYTW",
        },
        "liquid_bbb": {
            "total_return": "BAMLEM2RBBBLCRPIUSTRIV",
            "yield": "BAMLEM2RBBBLCRPIUSEY",
            "oas": "BAMLEM2RBBBLCRPIUSOAS",
            "yield_to_worst": "BAMLEM2RBBBLCRPIUSSYTW",
        },
        "aaa": {
            "total_return": "BAMLEM1BRRAAA2ACRPITRIV",
            "yield": "BAMLEM1BRRAAA2ACRPIEY",
            "oas": "BAMLEM1BRRAAA2ACRPIOAS",
            "yield_to_worst": "BAMLEM1BRRAAA2ACRPISYTW",
        },
        "bbb": {
            "total_return": "BAMLEM2BRRBBBCRPITRIV",
            "yield": "BAMLEM2BRRBBBCRPIEY",
            "oas": "BAMLEM2BRRBBBCRPIOAS",
            "yield_to_worst": "BAMLEM2BRRBBBCRPISYTW",
        },
        "bb": {
            "total_return": "BAMLEM3BRRBBCRPITRIV",
            "yield": "BAMLEM3BRRBBCRPIEY",
            "oas": "BAMLEM3BRRBBCRPIOAS",
            "yield_to_worst": "BAMLEM3BRRBBCRPISYTW",
        },
        "b": {
            "total_return": "BAMLEM4BRRBLCRPITRIV",
            "yield": "BAMLEM4BRRBLCRPIEY",
            "oas": "BAMLEM4BRRBLCRPIOAS",
            "yield_to_worst": "BAMLEM4BRRBLCRPISYTW",
        },
    },
}

BamlCategories = Literal["high_yield", "us", "emerging_markets"]
INDEX_CHOICES = [
    "corporate",
    "seasoned_corporate",
    "liquid_corporate",
    "yield_curve",
    "crossover",
    "public_sector",
    "private_sector",
    "non_financial",
    "high_grade",
    "high_yield",
    "liquid_emea",
    "emea",
    "liquid_asia",
    "asia",
    "liquid_latam",
    "latam",
    "liquid_aaa",
    "liquid_bbb",
    "aaa",
    "aa",
    "a",
    "bbb",
    "bb",
    "b",
    "ccc",
]

index_choices_str = "\n            ".join(INDEX_CHOICES)


class FredBondIndicesQueryParams(BondIndicesQueryParams):
    """FRED Bond Indices Query."""

    __json_schema_extra__ = {
        "index": {
            "multiple_items_allowed": True,
            "choices": sorted(INDEX_CHOICES),
        }
    }

    category: BamlCategories = Field(
        default="us",
        description="The type of index category. Used in conjunction with 'index', default is 'us'.",
    )
    index: str = Field(
        default="yield_curve",
        description="The specific index to query."
        + " Used in conjunction with 'category' and 'index_type', default is 'yield_curve'."
        + f"""
        Possible values are:
            {index_choices_str}\n
        """,
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
    _symbols: Optional[str] = PrivateAttr(default=None)


class FredBondIndicesData(BondIndicesData):
    """FRED Bond Indices Data."""

    maturity: Optional[str] = Field(
        default=None,
        description="The maturity range of the bond index."
        + " Only applicable when 'index' is 'yield_curve'.",
    )
    title: str = Field(
        description="The title of the index.",
    )


class FredBondIndicesFetcher(
    Fetcher[
        FredBondIndicesQueryParams,
        List[FredBondIndicesData],
    ]
):
    """FRED Bond Indices Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredBondIndicesQueryParams:
        """Transform query."""
        values = params.copy()
        new_index = []
        messages = []
        values.setdefault("index", "yield_curve")
        values.setdefault("category", "us")
        values.setdefault("index_type", "yield")
        is_yield_curve = False
        if "yield_curve" in values["index"]:
            values["category"] = "us"
            values["index"] = "yield_curve"
            new_index.append("yield_curve")
            is_yield_curve = True
            if (
                isinstance(values["index"], list)
                and len(values["index"] > 1)  # type: ignore
                or isinstance(values["index"], str)
                and "," in values["index"]
            ):
                message = "Multiple indices not allowed for: 'yield_curve'."
                messages.append(message)
        if is_yield_curve is False:
            indices = (
                values["index"]
                if isinstance(values["index"], list)
                else values["index"].split(",")
            )
            for index in indices:
                if values["category"] == "us":
                    if index not in BAML_CATEGORIES.get("us"):  # type: ignore
                        message = (
                            f"Invalid index, {index}, for category: 'us'."
                            + f" Must be one of {', '.join(BAML_CATEGORIES.get('us'))}."  # type: ignore
                        )
                        messages.append(message)
                    elif (
                        index == "seasoned_corporate"
                        and values["index_type"] != "yield"
                    ):
                        message = (
                            "Invalid index_type for index: 'seasoned_corporate'."
                            + " Must be 'yield'."
                        )
                        messages.append(message)
                    else:
                        new_index.append(index)
                if values["category"] == "high_yield":
                    if index not in ("us", "europe", "emerging"):
                        message = (
                            f"Invalid index, {index}, for category: 'high_yield'."
                            + f" Must be one of {', '.join(BAML_CATEGORIES.get('high_yield', ''))}."  # type: ignore
                        )
                        messages.append(message)
                    else:
                        new_index.append(index)
                if values["category"] == "emerging_markets":
                    if index not in BAML_CATEGORIES.get("emerging_markets"):  # type: ignore
                        message = (
                            f"Invalid index, {index}, for category: 'emerging_markets'."
                            + f" Must be one of {', '.join(BAML_CATEGORIES.get('emerging_markets', ''))}."  # type: ignore
                        )
                        messages.append(message)
                    else:
                        new_index.append(index)
        if not new_index:
            raise OpenBBError(
                "No valid combinations of parameters were found."
                + f"\n{','.join(messages) if messages else ''}"
            )
        if messages:
            warn(",".join(messages))

        symbols: List = []
        if "yield_curve" in values["index"]:
            maturities_dict = BAML_CATEGORIES[values["category"]][values["index"]]  # type: ignore
            maturities = list(maturities_dict)
            symbols = [
                maturities_dict[item][values["index_type"]] for item in maturities
            ]
        else:
            items = (
                values["index"]
                if isinstance(values["index"], list)
                else values["index"].split(",")
            )
            symbols = [
                BAML_CATEGORIES[values["category"]]  # type: ignore
                .get(item, {})
                .get(values["index_type"])
                for item in items
            ]
            symbols = [symbol for symbol in symbols if symbol]
        if not symbols:
            raise OpenBBError(
                "Error mapping the provided choices to series ID."
                + f"\n{','.join(messages) if messages else ''}"
            )
        values["index"] = ",".join(new_index)
        new_params = FredBondIndicesQueryParams(**values)
        new_params._symbols = ",".join(symbols)  # pylint: disable=protected-access

        return new_params

    @staticmethod
    async def aextract_data(
        query: FredBondIndicesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract data."""
        api_key = credentials.get("fred_api_key") if credentials else ""
        series_ids = query._symbols  # pylint: disable=protected-access
        credentials = {"fred_api_key": api_key}  # type: ignore
        item_query = dict(  # pylint: disable=R1735
            symbol=series_ids,
            start_date=query.start_date,
            end_date=query.end_date,
            frequency=query.frequency,
            aggregation_method=query.aggregation_method,
        )
        results: Dict = {}
        temp = await FredSeriesFetcher.fetch_data(item_query, credentials)
        result = [d.model_dump() for d in temp.result]
        results["metadata"] = temp.metadata
        results["data"] = result

        return results

    @staticmethod
    def transform_data(
        query: FredBondIndicesQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> AnnotatedResult[List[FredBondIndicesData]]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        from pandas import Categorical, DataFrame

        if not data:
            raise EmptyDataError("The request was returned empty.")
        df = DataFrame.from_records(data["data"])
        if df.empty:
            raise EmptyDataError(
                "No data found for the given query. Try adjusting the parameters."
            )
        # Flatten the data as a pivot table.
        df = (
            df.melt(id_vars="date", var_name="symbol", value_name="value")
            .query("value.notnull()")
            .set_index(["date", "symbol"])
            .sort_index()
            .reset_index()
        )
        # Normalize the percent values.
        if query.index_type != "total_return":
            df["value"] = df["value"] / 100

        titles_dict = {
            symbol: data["metadata"][symbol].get("title")
            for symbol in query._symbols.split(  # type: ignore  # pylint: disable=protected-access
                ","
            )
        }
        df["title"] = df.symbol.map(titles_dict)

        if query.index == "yield_curve":
            maturities_dict = BAML_CATEGORIES[query.category][query.index]  # type: ignore
            maturities = list(maturities_dict)
            maturity_dict = {
                maturities_dict[item][query.index_type]: item for item in maturities
            }
            df["maturity"] = df.symbol.map(maturity_dict)
            df["maturity"] = Categorical(
                df["maturity"],
                categories=maturities,
                ordered=True,
            )
            df = df.sort_values(by=["date", "maturity"]).reset_index(drop=True)

        records = df.to_dict(orient="records")
        metadata = data.get("metadata", {})

        return AnnotatedResult(
            result=[FredBondIndicesData.model_validate(r) for r in records],
            metadata=metadata,
        )
