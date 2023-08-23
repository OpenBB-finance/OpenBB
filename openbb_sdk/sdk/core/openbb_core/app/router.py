import warnings
from functools import partial
from inspect import Parameter, Signature, signature
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Type,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)

from fastapi import APIRouter, Depends
from importlib_metadata import entry_points
from pydantic import BaseModel
from pydantic.config import BaseConfig
from pydantic.validators import find_validators
from typing_extensions import Annotated, ParamSpec, _AnnotatedAlias

from openbb_core.app.env import Env
from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
    get_provider_interface,
)

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
        return isinstance(annotation, _AnnotatedAlias) and hasattr(
            annotation.__args__[0], "__dataclass_fields__"
        )

    @staticmethod
    def check_reserved_param(
        name: str,
        expected_annot: Any,
        parameter_map: Mapping[str, Parameter],
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

        check_reserved = partial(
            cls.check_reserved_param, parameter_map=parameter_map, func=func, sig=sig
        )
        check_reserved("cc", CommandContext)
        check_reserved("provider_choices", ProviderChoices)
        check_reserved("standard_params", StandardParams)
        check_reserved("extra_params", ExtraParams)

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

        if issubclass(return_type, OBBject):
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
                f"    {func.__name__}(...) -> OBBject[T] :\n"
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
        self._api_router = APIRouter(
            prefix=prefix,
            responses={404: {"description": "Not found"}},
        )

    @overload
    def command(self, func: Optional[Callable[P, OBBject]]) -> Callable[P, OBBject]:
        pass

    @overload
    def command(self, **kwargs) -> Callable:
        pass

    def command(
        self,
        func: Optional[Callable[P, OBBject]] = None,
        **kwargs,
    ) -> Optional[Callable]:
        if func is None:
            return lambda f: self.command(f, **kwargs)

        api_router = self._api_router

        model = kwargs.pop("model", "")
        if model:
            kwargs["response_model_exclude_unset"] = True
            kwargs["openapi_extra"] = {"model": model}

        func = SignatureInspector.complete_signature(func, model)
        if func is not None:
            CommandValidator.check(func=func)
            create_operation_id = [
                t.replace("_router", "")
                for t in func.__module__.split(".")[1:] + [func.__name__]
            ]
            cleaned_id = "_".join({c: "" for c in create_operation_id if c}.keys())

            kwargs["operation_id"] = kwargs.get("operation_id", cleaned_id)
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
        cls, func: Callable[P, OBBject], model: str
    ) -> Optional[Callable[P, OBBject]]:
        """Complete function signature."""
        provider_interface = get_provider_interface()
        return_type = func.__annotations__["return"]
        is_list = False

        results_type = get_type_hints(return_type)["results"]
        if not isinstance(results_type, type(None)):
            results_type = get_args(results_type)[0]

        is_list = get_origin(results_type) == list
        inner_type = results_type.__args__[0] if is_list else results_type

        func.__annotations__["return"].__doc__ = "OBBject"
        func.__annotations__["return"].__name__ = f"OBBject[{inner_type.__name__}]"

        if model:
            if model not in provider_interface.models:
                if Env().DEBUG_MODE:
                    warnings.warn(
                        message=f"\nSkipping api route '/{func.__name__}'.\n"
                        f"Model '{model}' not found.\n\n"
                        "Check available models in ProviderInterface().models",
                        category=OpenBBWarning,
                    )
                return None

            cls.validate_signature(
                func,
                {
                    "provider_choices": ProviderChoices,
                    "standard_params": StandardParams,
                    "extra_params": ExtraParams,
                },
            )

            func = cls.inject_dependency(
                func=func,
                arg="provider_choices",
                callable_=provider_interface.model_providers[model],
            )

            func = cls.inject_dependency(
                func=func,
                arg="standard_params",
                callable_=provider_interface.params[model]["standard"],
            )

            func = cls.inject_dependency(
                func=func,
                arg="extra_params",
                callable_=provider_interface.params[model]["extra"],
            )

            ReturnModel = merged_return = provider_interface.return_schema[model]

            if get_origin(provider_interface.return_map[model]) == list or is_list:
                ReturnModel = List[ReturnModel]  # type: ignore

            return_type = OBBject[ReturnModel]  # type: ignore
            return_type.__name__ = f"OBBject[{merged_return.__name__}]"
            return_type.__doc__ = (
                f"OBBject with results of type '{merged_return.__name__}'."
            )
            func.__annotations__["return"] = return_type
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
    def validate_signature(
        func: Callable[P, OBBject], expected: Dict[str, type]
    ) -> None:
        """Validate function signature before binding to model."""
        for k, v in expected.items():
            if k not in func.__annotations__:
                raise AttributeError(
                    f"Invalid signature: '{func.__name__}'. Missing '{k}' parameter."
                )

            if func.__annotations__[k] != v:
                raise TypeError(
                    f"Invalid signature: '{func.__name__}'. '{k}' parameter must be of type '{v.__name__}'."
                )

    @staticmethod
    def inject_dependency(
        func: Callable[P, OBBject], arg: str, callable_: Any
    ) -> Callable[P, OBBject]:
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

    def __init__(
        self, router: Optional[Router] = None, coverage_sep: Optional[str] = None
    ) -> None:
        self._router = router or RouterLoader.from_extensions()
        self._map = self.get_command_map(router=self._router)
        self._provider_coverage = self.get_provider_coverage(
            router=self._router, sep=coverage_sep
        )
        self._command_coverage = self.get_command_coverage(
            router=self._router, sep=coverage_sep
        )

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
    def get_command_map(
        router: Router,
    ) -> Dict[str, Callable]:
        api_router = router.api_router
        command_map = {route.path: route.endpoint for route in api_router.routes}  # type: ignore
        return command_map

    @staticmethod
    def get_provider_coverage(
        router: Router, sep: Optional[str] = None
    ) -> Dict[str, List[str]]:
        api_router = router.api_router

        mapping = get_provider_interface().map

        coverage_map: Dict[Any, Any] = {}
        for route in api_router.routes:
            openapi_extra = getattr(route, "openapi_extra")
            if openapi_extra:
                model = openapi_extra.get("model", None)
                if model:
                    providers = list(mapping[model].keys())
                    if "openbb" in providers:
                        providers.remove("openbb")
                    for provider in providers:
                        if provider not in coverage_map:
                            coverage_map[provider] = []
                        if hasattr(route, "path"):
                            rp = (
                                route.path  # type: ignore
                                if sep is None
                                else route.path.replace("/", sep)  # type: ignore
                            )
                            coverage_map[provider].append(rp)

        return coverage_map

    @staticmethod
    def get_command_coverage(
        router: Router, sep: Optional[str] = None
    ) -> Dict[str, List[str]]:
        api_router = router.api_router

        mapping = get_provider_interface().map

        coverage_map: Dict[Any, Any] = {}
        for route in api_router.routes:
            openapi_extra = getattr(route, "openapi_extra")
            if openapi_extra:
                model = openapi_extra.get("model", None)
                if model:
                    providers = list(mapping[model].keys())
                    if "openbb" in providers:
                        providers.remove("openbb")

                    if hasattr(route, "path"):
                        rp = (
                            route.path if sep is None else route.path.replace("/", sep)  # type: ignore
                        )
                        if route.path not in coverage_map:  # type: ignore
                            coverage_map[rp] = []
                        coverage_map[rp] = providers
        return coverage_map

    def get_command(self, route: str) -> Optional[Callable]:
        return self._map.get(route, None)


class LoadingError(Exception):
    """Error loading extension."""


class RouterLoader:
    @staticmethod
    def from_extensions() -> Router:
        router = Router()

        for entry_point in entry_points(group="openbb_core_extension"):
            try:
                router.include_router(
                    router=entry_point.load(), prefix=f"/{entry_point.name}"
                )
            except Exception as e:
                raise LoadingError(
                    f"Invalid extension '{entry_point.name}': {e}"
                ) from e

        return router
