"""OpenBB Platform example generator."""

from typing import (
    Any,
    Dict,
    Literal,
    get_origin,
)

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined


class ExampleGenerator:
    """Generate examples for the API."""

    @staticmethod
    def get_model_standard_params(param_fields: Dict[str, FieldInfo]) -> Dict[str, Any]:
        """Get the test params for the fetcher based on the required standard params."""
        test_params: Dict[str, Any] = {}
        for field_name, field in param_fields.items():
            if field.default and field.default is not PydanticUndefined:
                test_params[field_name] = field.default
            elif field.default and field.default is PydanticUndefined:
                example_dict = {
                    "symbol": "AAPL",
                    "symbols": "AAPL,MSFT",
                    "start_date": "2023-01-01",
                    "end_date": "2023-06-06",
                    "country": "Portugal",
                    "date": "2023-01-01",
                    "countries": ["portugal", "spain"],
                }
                if field_name in example_dict:
                    test_params[field_name] = example_dict[field_name]
                elif field.annotation == str:
                    test_params[field_name] = "TEST_STRING"
                elif field.annotation == int:
                    test_params[field_name] = 1
                elif field.annotation == float:
                    test_params[field_name] = 1.0
                elif field.annotation == bool:
                    test_params[field_name] = True
                elif get_origin(field.annotation) is Literal:  # type: ignore
                    option = field.annotation.__args__[0]  # type: ignore
                    if isinstance(option, str):
                        test_params[field_name] = f'"{option}"'
                    else:
                        test_params[field_name] = option

        return test_params

    @classmethod
    def generate_example(
        cls,
        route: str,
        standard_params: Dict[str, FieldInfo],
    ) -> str:
        """Generate the example for the command."""
        if not route:
            return ""

        example_params = cls.get_model_standard_params(param_fields=standard_params)

        # Edge cases (might find more)
        if "crypto" in route[0] and "symbol" in example_params:
            example_params["symbol"] = "BTCUSD"
        elif "currency" in route[0] and "symbol" in example_params:
            example_params["symbol"] = "EURUSD"
        elif (
            "index" in route[0]
            and "european" not in route[0]
            and "symbol" in example_params
        ):
            example_params["symbol"] = "SPX"
        elif (
            "index" in route[0]
            and "european" in route[0]
            and "symbol" in example_params
        ):
            example_params["symbol"] = "BUKBUS"
        elif (
            "futures" in route[0] and "curve" in route[0] and "symbol" in example_params
        ):
            example_params["symbol"] = "VX"
        elif "futures" in route[0] and "symbol" in example_params:
            example_params["symbol"] = "ES"

        example = f"obb.{route}("
        for param_name, param_value in example_params.items():
            if isinstance(param_value, str):
                param_value = f'"{param_value}"'  # noqa: PLW2901
            example += f"{param_name}={param_value}, "
        if example_params:
            example = example[:-2] + ")\n"
        else:
            example += ")"

        return example
