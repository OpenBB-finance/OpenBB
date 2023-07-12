import sys
from functools import partial
from inspect import Parameter, Signature, signature
from types import MappingProxyType
from typing import (
    Annotated,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)

import pkg_resources
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pydantic.config import BaseConfig
from pydantic.validators import find_validators

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
    get_provider_interface,
)

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

P = ParamSpec("P")


class CommandValidator:
    @staticmethod
    def is_standard_pydantic_type(value_type: Type) -> bool:
        """Check whether or not a parameter type is a valid Pydantic Standard Type."""

        class ArbitraryTypesAllowed(BaseConfig):
            arbitrary_types_allowed = True

        func = next(find_validators(value_type, config=ArbitraryTypesAllowed))
        valid_type = func.__name__ != "arbitrary_type_validator"

        return valid_type

    @staticmethod
    def is_valid_pydantic_model_type(model_type: Type) -> bool:
        if issubclass(model_type, BaseModel):
            try:
                model_type.schema_json()
                return True
            except ValueError:
                return False
        else:
            return False

    @classmethod
    def is_serializable_value_type(cls, value_type: Type) -> bool:
        return cls.is_standard_pydantic_type(
            value_type=value_type
        ) or cls.is_valid_pydantic_model_type(model_type=value_type)

    @staticmethod
    def is_annotated_dc(annotation) -> bool:
        return get_origin(annotation) == Annotated and hasattr(
            annotation.__args__[0], "__dataclass_fields__"
        )

    @staticmethod
    def check_reserved_param(
        name: str,
        expected_annot: Any,
        parameter_map: MappingProxyType[str, Parameter],
        func: Callable,
        sig: Signature,
    ):
        if name in parameter_map:
            annotation = getattr(parameter_map[name], "annotation", None)
            if annotation is not None and CommandValidator.is_annotated_dc(annotation):
                annotation = annotation.__args__[0].__bases__[0]
            if not annotation == expected_annot:
                raise TypeError(
                    f"The parameter `{name}` must be a {expected_annot}.\n"
                    f"module    = {func.__module__}\n"
                    f"function  = {func.__name__}\n"
                    f"signature = {sig}\n"
                )

    @classmethod
    def check_parameters(cls, func: Callable):
        sig = signature(func)
        parameter_map = sig.parameters

        check_res = partial(
            cls.check_reserved_param, parameter_map=parameter_map, func=func, sig=sig
        )
        check_res("cc", CommandContext)
        check_res("provider_choices", ProviderChoices)
        check_res("standard_params", StandardParams)
        check_res("extra_params", ExtraParams)

        for parameter in parameter_map.values():
            if not cls.is_serializable_value_type(value_type=parameter.annotation):
                raise TypeError(
                    "Invalid parameter type, please provide a serializable type like:"
                    "BaseModel, Pydantic Standard Type or CommandContext.\n"
                    f"module    = {func.__module__}\n"
                    f"function  = {func.__name__}\n"
                    f"signature = {sig}\n"
                    f"parameter = {parameter}\n"
                )

    @classmethod
    def check_return(cls, func: Callable):
        sig = signature(func)
        return_type = sig.return_annotation

        if issubclass(return_type, CommandOutput):
            results_type = get_type_hints(return_type)["results"]
            if isinstance(results_type, type(None)):
                valid_return_type = False
            else:
                generic_type_list = get_args(results_type)
                valid_return_type = cls.is_serializable_value_type(
                    value_type=generic_type_list[0]
                )
        else:
            valid_return_type = False

        if not valid_return_type:
            raise TypeError(
                "\nInvalid function: "
                f"    {func.__module__}.{func.__name__}\n"
                "Invalid return type in signature:"
                f"    {func.__name__}(...) -> {sig.return_annotation}:\n"
                "Allowed return type:"
                f"    {func.__name__}(...) -> CommandOutput[T] :\n"
                "If you need T = None, use an empty model instead.\n"
            )

    @classmethod
    def check(cls, func: Callable):
        cls.check_parameters(func=func)
        cls.check_return(func=func)


class Router:
    @property
    def api_router(self) -> APIRouter:
        return self._api_router

    def __init__(
        self,
        prefix: str = "",
    ) -> None:
        self._api_router = APIRouter(prefix=prefix)

    @overload
    def command(
        self, func: Optional[Callable[P, CommandOutput]]
    ) -> Callable[P, CommandOutput]:
        pass

    @overload
    def command(self, **kwargs) -> Callable:
        pass

    def command(
        self,
        func: Optional[Callable[P, CommandOutput]] = None,
        **kwargs,
    ) -> Callable:
        if func is None:
            return lambda f: self.command(f, **kwargs)

        api_router = self._api_router

        query = kwargs.pop("query", "")
        if query:
            kwargs["response_model_exclude_unset"] = True
            kwargs["openapi_extra"] = {"query": query}

        func = SignatureInspector.complete_signature(func, query)

        CommandValidator.check(func=func)

        kwargs["path"] = kwargs.get("path", f"/{func.__name__}")
        kwargs["endpoint"] = func
        kwargs["methods"] = kwargs.get("methods", ["GET"])
        kwargs["description"] = SignatureInspector.get_description(func)

        api_router.add_api_route(**kwargs)

        return func

    def include_router(
        self,
        router: "Router",
        prefix: str = "",
    ):
        tags = [prefix[1:]] if prefix else None
        self._api_router.include_router(
            router=router.api_router, prefix=prefix, tags=tags  # type: ignore
        )


class SignatureInspector:
    @classmethod
    def complete_signature(
        cls, func: Callable[P, CommandOutput], query: str
    ) -> Callable[P, CommandOutput]:
        """Complete function signature."""
        provider_interface = get_provider_interface()
        if query:
            if query not in provider_interface.queries:
                raise AttributeError(
                    f"Invalid query: {query}. Check available queries in ProviderInterface().queries"
                )

            cls.validate_signature(func=func)

            func = cls.inject_dependency(
                func=func,
                arg="provider_choices",
                callable_=provider_interface.query_providers[query],
            )

            func = cls.inject_dependency(
                func=func,
                arg="standard_params",
                callable_=provider_interface.params[query]["standard"],
            )

            func = cls.inject_dependency(
                func=func,
                arg="extra_params",
                callable_=provider_interface.params[query]["extra"],
            )

            data_type = provider_interface.merged_data[query]
            func.__annotations__["return"] = CommandOutput[List[data_type]]  # type: ignore
        elif (
            "provider_choices" in func.__annotations__
            and func.__annotations__["provider_choices"] == ProviderChoices
        ):
            func = cls.inject_dependency(
                func=func,
                arg="provider_choices",
                callable_=provider_interface.provider_choices,
            )
        return func

    @staticmethod
    def validate_signature(func: Callable[P, CommandOutput]) -> None:
        """Validate function signature before binding to query."""
        if "provider_choices" not in func.__annotations__:
            raise AttributeError(
                f"Invalid signature: {func.__name__}. Missing provider_choices parameter."
            )

        if func.__annotations__["provider_choices"] != ProviderChoices:
            raise TypeError(
                f"Invalid signature: {func.__name__}. provider_choices parameter must be of type ProviderChoices."
            )

        if "standard_params" not in func.__annotations__:
            raise AttributeError(
                f"Invalid signature: {func.__name__}. Missing standard_params parameter."
            )

        if func.__annotations__["standard_params"] != StandardParams:
            raise TypeError(
                f"Invalid signature: {func.__name__}. standard_params parameter must be of type StandardParams."
            )

        if "extra_params" not in func.__annotations__:
            raise AttributeError(
                f"Invalid signature: {func.__name__}. Missing extra_params parameter."
            )

        if func.__annotations__["extra_params"] != ExtraParams:
            raise TypeError(
                f"Invalid signature: {func.__name__}. extra_params parameter must be of type ExtraParams."
            )

    @staticmethod
    def inject_dependency(
        func: Callable[P, CommandOutput], arg: str, callable_: Any
    ) -> Callable[P, CommandOutput]:
        """Annotate function with dependency injection."""
        func.__annotations__[arg] = Annotated[callable_, Depends()]  # type: ignore
        return func

    @staticmethod
    def get_description(func: Callable) -> str:
        """Get description from docstring."""
        doc = func.__doc__
        if doc:
            description = doc.split("    Parameters\n    ----------")[0]
            description = description.split("    Returns\n    -------")[0]
            description = "\n".join([line.strip() for line in description.split("\n")])

            return description
        return ""


class CommandMap:
    """Matching Routes with Commands."""

    def __init__(self, router: Optional[Router] = None) -> None:
        self._router = router or RouterLoader.from_plugins()
        self._map = self.get_command_map(router=self._router)
        self._provider_coverage = self.get_provider_coverage(router=self._router)
        self._command_coverage = self.get_command_coverage(router=self._router)

    @property
    def map(self) -> Dict[str, Callable]:
        return self._map

    @property
    def provider_coverage(self) -> Dict[str, List[str]]:
        return self._provider_coverage

    @property
    def command_coverage(self) -> Dict[str, List[str]]:
        return self._command_coverage

    @staticmethod
    def get_command_map(router: Router) -> Dict[str, Callable]:
        api_router = router.api_router
        command_map = {route.path: route.endpoint for route in api_router.routes}  # type: ignore
        return command_map

    @staticmethod
    def get_provider_coverage(router: Router) -> Dict[str, List[str]]:
        api_router = router.api_router

        mapping = get_provider_interface().map

        coverage_map: Dict[Any, Any] = {}
        for route in api_router.routes:
            openapi_extra = getattr(route, "openapi_extra")
            if openapi_extra:
                query = openapi_extra.get("query", None)
                if query:
                    providers = list(mapping[query].keys())
                    if "openbb" in providers:
                        providers.remove("openbb")
                    for provider in providers:
                        if provider not in coverage_map:
                            coverage_map[provider] = []
                        if hasattr(route, "path"):
                            coverage_map[provider].append(route.path)

        return coverage_map

    @staticmethod
    def get_command_coverage(router: Router) -> Dict[str, List[str]]:
        api_router = router.api_router

        mapping = get_provider_interface().map

        coverage_map: Dict[Any, Any] = {}
        for route in api_router.routes:
            openapi_extra = getattr(route, "openapi_extra")
            if openapi_extra:
                query = openapi_extra.get("query", None)
                if query:
                    providers = list(mapping[query].keys())
                    if "openbb" in providers:
                        providers.remove("openbb")

                    if hasattr(route, "path"):
                        if route.path not in coverage_map:
                            coverage_map[route.path] = []
                        coverage_map[route.path] = providers
        return coverage_map

    def get_command(self, route: str) -> Optional[Callable]:
        return self._map.get(route, None)


class RouterLoader:
    @staticmethod
    def from_plugins() -> Router:
        router = Router()
        for entry_point in pkg_resources.iter_entry_points("openbb_sdk_core_extension"):
            try:
                router.include_router(
                    router=entry_point.load(),
                    prefix=f"/{entry_point.name}",
                )
            except Exception as e:
                raise ModuleNotFoundError(
                    f"Invalid extension {entry_point.name}: {e}"
                ) from e

        return router
