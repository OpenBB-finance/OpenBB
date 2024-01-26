"""OpenBB Platform example generator."""

from typing import (
    Any,
    Dict,
)

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from openbb_core.app.provider_interface import ProviderInterface

# The example parameters can be defined for:
#
# route:
#   "crypto.historical.price": {
#       "symbol": "BTCUSD",
#   }
#
# router:
#   "crypto": {
#       "symbol": "ETHUSD",
#   }
#
#   "crypto.historical": {
#       "symbol": "ETHUSD",
#   }
#
# The route has priority over the router.

POOL = {
    "crypto": {
        "symbol": "BTCUSD",
    },
    "currency": {
        "symbol": "EURUSD",
    },
    "derivatives": {
        "symbol": "AAPL",
    },
    "economy": {
        "country": "portugal",
        "countries": ["portugal", "spain"],
    },
    "economy.fred_series": {
        "symbol": "GFDGDPA188S",
    },
    "equity": {
        "symbol": "AAPL",
        "symbols": "AAPL,MSFT",
        "query": "AAPL",
    },
    "equity.fundamental.historical_attributes": {
        "tag": "ebitda",
    },
    "equity.fundamental.latest_attributes": {
        "tag": "ceo",
    },
    "equity.fundamental.transcript": {
        "year": 2020,
    },
    "etf": {
        "symbol": "SPY",
        "query": "Vanguard",
    },
    "futures": {
        "symbol": "ES",
    },
    "index": {
        "symbol": "SPX",
        "index": "^IBEX",
    },
    "news": {
        "symbols": "AAPL,MSFT",
    },
    "regulators": {
        "symbol": "AAPL",
        "query": "AAPL",
    },
}


class ExampleGenerator:
    """Generate examples for the API."""

    @staticmethod
    def _get_value_from_pool(pool, key, param):
        keys = key.split(".")
        for i in range(len(keys), 0, -1):
            partial_key = ".".join(keys[:i])
            if partial_key in pool:
                if param in pool[partial_key]:
                    return pool[partial_key][param]
        return "VALUE_NOT_FOUND"

    @classmethod
    def generate(
        cls,
        route: str,
        model: str,
    ) -> str:
        """Generate the example for the command."""
        if not route or not model:
            return ""

        standard_params: Dict[str, FieldInfo] = (
            ProviderInterface()
            .map.get(model, {})
            .get("openbb", {})
            .get("QueryParams", {})
            .get("fields", {})
        )

        eg_params: Dict[str, Any] = {}
        for p, v in standard_params.items():
            if v.default is not None:
                if v.default is not PydanticUndefined and v.default != "":
                    eg_params[p] = v.default
                else:
                    eg_params[p] = cls._get_value_from_pool(POOL, route, p)

        example = f"obb.{route}("
        for n, v in eg_params.items():
            if isinstance(v, str):
                v = f'"{v}"'  # noqa: PLW2901
            example += f"{n}={v}, "
        if eg_params:
            example = example[:-2] + ")"
        else:
            example += ")"

        return example
