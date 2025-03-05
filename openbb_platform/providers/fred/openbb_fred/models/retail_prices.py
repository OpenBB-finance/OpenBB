"""FRED Retail Prices Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional, Union

from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.retail_prices import (
    RetailPricesData,
    RetailPricesQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fred.models.series import FredSeriesFetcher
from pydantic import Field, field_validator

PRICES_MEATS = [
    "bacon",
    "beef",
    "chicken",
    "chops",
    "ham",
    "pork",
    "steak",
    "usda",
]
PRICES_DAIRY = [
    "butter",
    "cheese",
    "eggs",
    "ice_cream",
    "milk",
    "yogurt",
]
PRICES_CEREALS = [
    "bread",
    "cookies",
    "flour",
    "rice",
    "spaghetti",
    "sugar",
]
PRICES_PRODUCE = [
    "bananas",
    "beans",
    "corn",
    "grapefruit",
    "lemons",
    "lettuce",
    "oranges",
    "potato_chips",
    "potatoes",
    "strawberries",
    "tomatoes",
]
PRICES_BEVERAGES = [
    "beer",
    "coffee",
    "malt_beverages",
    "vodka",
    "orange_juice",
    "soft_drinks",
    "wine",
]
PRICES_FUEL = [
    "diesel",
    "electricity",
    "gasoline",
    "oil",
    "utility",
]
ALL_ITEMS = [
    "beverages",
    "cereals",
    "dairy",
    "fuel",
    "meats",
    "produce",
    "bacon",
    "bananas",
    "beans",
    "beef",
    "beer",
    "bread",
    "butter",
    "cheese",
    "chicken",
    "chops",
    "coffee",
    "cookies",
    "corn",
    "diesel",
    "eggs",
    "electricity",
    "flour",
    "gas",
    "gasoline",
    "grapefruit",
    "groud_beef",
    "ham",
    "ice_cream",
    "lemons",
    "lettuce",
    "malt_beverages",
    "milk",
    "oil",
    "orange_juice",
    "oranges",
    "potato_chips",
    "potatoes",
    "pork",
    "rice",
    "soft_drinks",
    "spaghetti",
    "steak",
    "strawberries",
    "sugar",
    "tomatoes",
    "unleaded",
    "usda",
    "vodka",
    "wine",
    "yogurt",
]
AllItems = Literal[
    "beverages",
    "cereals",
    "dairy",
    "fuel",
    "produce",
    "meats",
    "bacon",
    "bananas",
    "beans",
    "beef",
    "beer",
    "bread",
    "butter",
    "cheese",
    "chicken",
    "chops",
    "coffee",
    "cookies",
    "corn",
    "diesel",
    "eggs",
    "electricity",
    "flour",
    "gas",
    "gasoline",
    "grapefruit",
    "ground_beef",
    "ham",
    "ice_cream",
    "lemons",
    "lettuce",
    "malt_beverages",
    "milk",
    "oil",
    "orange_juice",
    "oranges",
    "pork",
    "potato_chips",
    "potatoes",
    "rice",
    "soft_drinks",
    "spaghetti",
    "steak",
    "strawberries",
    "sugar",
    "tomatoes",
    "unleaded",
    "usda",
    "vodka",
    "wine",
    "yogurt",
]
REGIONS = [
    "all_city",
    "northeast",
    "midwest",
    "south",
    "west",
]
Regions = Literal[
    "all_city",
    "northeast",
    "midwest",
    "south",
    "west",
]
regions_dict = {
    "all_city": "average_prices_city_average",
    "midwest": "average_prices_midwest_urban",
    "northeast": "average_prices_northeast_urban",
    "south": "average_prices_south_urban",
    "west": "average_prices_west_urban",
}
frequency_dict = {
    "annual": "a",
    "quarter": "q",
    "monthly": "m",
}


class FredRetailPricesQueryParams(RetailPricesQueryParams):
    """FRED Retail Prices Query Parameters."""

    __json_schema_extra__ = {
        "item": {"multiple_items_allowed": False, "choices": ALL_ITEMS},
        "country": {"multiple_items_allowed": False, "choices": ["united_states"]},
    }

    item: AllItems = Field(
        default="fuel",
        description="The item or basket of items to query.",
    )
    country: Literal["united_states"] = Field(
        default="united_states",
        description=QUERY_DESCRIPTIONS.get("country", ""),
    )
    region: Regions = Field(
        default="all_city",
        description="The region to get average price levels for.",
    )
    frequency: Literal["annual", "quarter", "monthly"] = Field(
        default="monthly",
        description=QUERY_DESCRIPTIONS.get("frequency"),
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
    )

    @field_validator("item", mode="before", check_fields=False)
    @classmethod
    def validate_item(cls, v):
        """Validate the default state."""
        if v is None:
            return "fuel"
        return v


class FredRetailPricesData(RetailPricesData):
    """FRED Retail Prices Data."""


class FredRetailPricesFetcher(
    Fetcher[FredRetailPricesQueryParams, List[FredRetailPricesData]]
):
    """FRED Retail Prices Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FredRetailPricesQueryParams:
        """Transform query."""
        return FredRetailPricesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredRetailPricesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        import json
        from importlib.resources import files

        frequency = frequency_dict.get(query.frequency)
        transform = query.transform
        region = regions_dict[query.region]

        resource_path = files("openbb_fred.utils").joinpath(f"{region}.json")

        with resource_path.open() as p:
            all_symbols = json.load(p)

        items_dict = {
            "beverages": PRICES_BEVERAGES,
            "cereals": PRICES_CEREALS,
            "dairy": PRICES_DAIRY,
            "fuel": PRICES_FUEL,
            "produce": PRICES_PRODUCE,
            "meats": PRICES_MEATS,
            "all_items": ALL_ITEMS,
        }
        # Get the series IDs for each item in the group.
        series: List = []
        items_list = items_dict.get(query.item, [query.item])
        for k, v in all_symbols.items():
            for price in list(set(items_list)):
                if price.replace("_", " ") in v.lower():
                    series.append(k)

        response = await FredSeriesFetcher.fetch_data(
            dict(
                symbol=",".join(series),
                start_date=query.start_date,
                end_date=query.end_date,
                frequency=frequency,
                transform=transform,
            ),
            credentials,
        )
        if not response.result:
            raise EmptyDataError(
                "No data found for the item and region combination."
                + " You may also be experiencing rate limiting."
                + " Please adjust the parameters or try again in a few minutes."
            )
        return {
            "metadata": response.metadata,
            "data": [d.model_dump() for d in response.result],
        }

    @staticmethod
    def transform_data(
        query: FredRetailPricesQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> AnnotatedResult[List[FredRetailPricesData]]:
        """Transform data."""
        # pylint: disable=import-outside-toplevel
        import json  # noqa
        from importlib.resources import files  # noqa
        from pandas import DataFrame  # noqa

        region = regions_dict[query.region]

        resource_path = files("openbb_fred.utils").joinpath(f"{region}.json")

        with resource_path.open() as p:
            all_symbols = json.load(p)

        df = DataFrame(data["data"])
        metadata = data["metadata"]
        # Flatten data
        df = df.melt(id_vars="date", var_name="description", value_name="value").query(
            "value.notnull()"
        )
        df["symbol"] = df["description"].copy()
        # Map the description to the symbol
        df.description = df.description.map(all_symbols).str.strip()
        # Normalize percent values
        if query.transform in ["pch", "pc1", "pca", "cch", "cca"]:
            df["value"] = df["value"] / 100
        df["country"] = "united_states"
        df = df.set_index(["date", "description"]).sort_index().reset_index()
        records = df.to_dict(orient="records")

        return AnnotatedResult(
            result=[FredRetailPricesData.model_validate(d) for d in records],
            metadata=metadata,
        )
