from inspect import Parameter, isclass
from typing import Any, Callable, Dict, List, Literal, Optional, OrderedDict, get_origin

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap


class DocstringGenerator:
    """Dynamically generate docstrings for the commands."""

    provider_interface = ProviderInterface()

    @staticmethod
    def get_OBBject_description(results_type: str, providers: Optional[str]) -> str:
        """Get the command output description."""
        available_providers = providers or "Optional[str]"

        obbject_description = (
            "    OBBject\n"
            f"        results : {results_type}\n"
            "            Serializable results.\n"
            f"        provider : {available_providers}\n"
            "            Provider name.\n"
            "        warnings : Optional[List[Warning_]]\n"
            "            List of warnings.\n"
            "        chart : Optional[Chart]\n"
            "            Chart object.\n"
            "        extra : Dict[str, Any]\n"
            "            Extra info.\n"
        )
        obbject_description = obbject_description.replace("NoneType", "None")

        return obbject_description

    @classmethod
    def generate_model_docstring(
        cls,
        model_name: str,
        summary: str,
        explicit_params: dict,
        params: dict,
        returns: Dict[str, FieldInfo],
        results_type: str,
        examples: Optional[List[str]] = None,
    ) -> str:
        """Create the docstring for model."""

        def format_type(type_: str, char_limit: Optional[int] = None) -> str:
            """Format type in docstrings."""
            type_str = str(type_)
            type_str = type_str.replace("NoneType", "None")
            if char_limit:
                type_str = type_str[:char_limit] + (
                    "..." if len(str(type_str)) > char_limit else ""
                )
            return type_str

        def format_description(description: str) -> str:
            """Format description in docstrings."""
            description = description.replace("\n", "\n    ")
            return description

        standard_dict = params["standard"].__dataclass_fields__
        extra_dict = params["extra"].__dataclass_fields__

        if examples:
            example_docstring = "\n    Example\n    -------\n"
            example_docstring += "    >>> from openbb import obb\n"
            for example in examples:
                example_docstring += f"    >>> {example}\n"

        docstring = summary.strip("\n")
        docstring += "\n\n"
        docstring += "    Parameters\n"
        docstring += "    ----------\n"

        # Explicit parameters
        for param_name, param in explicit_params.items():
            if param_name in standard_dict:
                # pylint: disable=W0212
                p_type = param._annotation.__args__[0]
                type_ = p_type.__name__ if isclass(p_type) else p_type
                description = getattr(
                    param._annotation.__metadata__[0], "description", ""
                )
            elif param_name == "provider":
                # pylint: disable=W0212
                type_ = param._annotation
                default = param._annotation.__args__[0].__args__[0]
                description = f"""The provider to use for the query, by default None.
    If None, the provider specified in defaults is selected or '{default}' if there is
    no default."""
            elif param_name == "chart":
                type_ = "bool"
                description = "Whether to create a chart or not, by default False."
            else:
                type_ = ""
                description = ""

            type_str = format_type(type_, char_limit=79)  # type: ignore
            docstring += f"    {param_name} : {type_str}\n"
            docstring += f"        {format_description(description)}\n"

        # Kwargs
        for param_name, param in extra_dict.items():
            p_type = param.type
            type_ = p_type.__name__ if isclass(p_type) else p_type

            if "NoneType" in str(type_):
                type_ = f"Optional[{type_}]".replace(", NoneType", "")

            description = getattr(param.default, "description", "")

            docstring += f"    {param_name} : {type_}\n"
            docstring += f"        {format_description(description)}\n"

        # Returns
        docstring += "\n"
        docstring += "    Returns\n"
        docstring += "    -------\n"
        provider_param = explicit_params.get("provider", None)
        available_providers = getattr(provider_param, "_annotation", None)

        docstring += cls.get_OBBject_description(results_type, available_providers)

        # Schema
        underline = "-" * len(model_name)
        docstring += f"\n    {model_name}\n    {underline}\n"

        for name, field in returns.items():
            try:
                _type = field.annotation
                is_optional = not field.is_required()
                if "BeforeValidator" in str(_type):
                    _type = "Optional[int]" if is_optional else "int"  # type: ignore

                field_type = (
                    str(_type)
                    .replace("<class '", "")
                    .replace("'>", "")
                    .replace("typing.", "")
                    .replace("pydantic.types.", "")
                    .replace("datetime.datetime", "datetime")
                    .replace("datetime.date", "date")
                    .replace("NoneType", "None")
                    .replace(", None", "")
                )
                field_type = (
                    f"Optional[{field_type}]"
                    if is_optional and "Optional" not in str(_type)
                    else field_type
                )
            except TypeError:
                # Fallback to the annotation if the repr fails
                field_type = field.annotation  # type: ignore

            description = getattr(field, "description", "")

            docstring += f"    {field.alias or name} : {field_type}\n"
            docstring += f"        {format_description(description)}\n"

        if examples:
            docstring += example_docstring

        return docstring

    @classmethod
    def generate(
        cls,
        func: Callable,
        formatted_params: OrderedDict[str, Parameter],
        model_name: Optional[str] = None,
        examples: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Generate the docstring for the function."""
        doc = func.__doc__
        if model_name:
            params = cls.provider_interface.params.get(model_name, None)
            return_schema = cls.provider_interface.return_schema.get(model_name, None)
            if params and return_schema:
                explicit_dict = dict(formatted_params)
                explicit_dict.pop("extra_params", None)

                returns = return_schema.model_fields
                results_type = func.__annotations__.get("return", model_name)
                if hasattr(results_type, "results_type_repr"):
                    results_type = results_type.results_type_repr()

                return cls.generate_model_docstring(
                    model_name=model_name,
                    summary=func.__doc__ or "",
                    explicit_params=explicit_dict,
                    params=params,
                    returns=returns,
                    results_type=results_type,
                    examples=examples,
                )
            return doc
        if examples and examples != [""] and doc:
            doc += "\n    Examples\n    --------\n"
            doc += "    >>> from openbb import obb\n"
            for example in examples:
                if example != "":
                    doc += f"    >>> {example}\n"
        return doc

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

    @staticmethod
    def get_full_command_name(route: str) -> str:
        """Get the full command name."""
        cmd_parts = route.split("/")
        del cmd_parts[0]

        menu = cmd_parts[0]
        command = cmd_parts[-1]
        sub_menus = cmd_parts[1:-1]

        sub_menu_str_cmd = f".{'.'.join(sub_menus)}" if sub_menus else ""

        full_command = f"{menu}{sub_menu_str_cmd}.{command}"

        return full_command

    @classmethod
    def generate_example(
        cls,
        model_name: str,
        standard_params: Dict[str, FieldInfo],
    ) -> str:
        """Generate the example for the command."""
        # find the model router here
        cm = CommandMap()
        commands_model = cm.commands_model
        route = [k for k, v in commands_model.items() if v == model_name]

        if not route:
            return ""

        full_command_name = cls.get_full_command_name(route=route[0])
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

        example = "\n        Example\n        -------\n"
        example += "        >>> from openbb import obb\n"
        example += f"        >>> obb.{full_command_name}("
        for param_name, param_value in example_params.items():
            if isinstance(param_value, str):
                param_value = f'"{param_value}"'  # noqa: PLW2901
            example += f"{param_name}={param_value}, "
        if example_params:
            example = example[:-2] + ")\n"
        else:
            example += ")\n"

        return example
