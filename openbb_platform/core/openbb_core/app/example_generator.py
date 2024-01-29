"""OpenBB Platform example generator."""

import json
from pathlib import Path
from typing import (
    Any,
    Dict,
)

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from openbb_core.app.constants import ASSETS_DIRECTORY
from openbb_core.app.provider_interface import ProviderInterface

try:
    with Path(ASSETS_DIRECTORY, "parameter_pool.json").open() as f:
        PARAMETER_POOL = json.load(f)
except Exception:
    PARAMETER_POOL = {}


class ExampleGenerator:
    """Generate examples for the API."""

    @staticmethod
    def _get_value_from_pool(pool: dict, route: str, param: str) -> str:
        """Get the value from the pool.

        The example parameters can be defined for:
        - route: "crypto.historical.price": {"symbol": "CRYPTO_HISTORICAL_PRICE_SYMBOL"}
        - sub-router: "crypto.historical": {"symbol": "CRYPTO_HISTORICAL_SYMBOL"}
        - router: "crypto": {"symbol": "CRYPTO_SYMBOL"}

        The search for the 'key' is done in the following order:
        - route
        - sub-router
        - router
        """
        parts = route.split(".")
        for i in range(len(parts), 0, -1):
            partial_route = ".".join(parts[:i])
            if partial_route in pool and param in pool[partial_route]:
                return pool[partial_route][param]
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
                    eg_params[p] = cls._get_value_from_pool(PARAMETER_POOL, route, p)

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
