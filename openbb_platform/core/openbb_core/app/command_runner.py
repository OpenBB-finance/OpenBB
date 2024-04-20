"""Command runner module."""

# pylint: disable=R0903

from copy import deepcopy
from dataclasses import asdict, is_dataclass
from datetime import datetime
from inspect import Parameter, signature
from sys import exc_info
from time import perf_counter_ns
from typing import Any, Callable, Dict, List, Optional, Tuple, Type
from warnings import catch_warnings, showwarning, warn

from pydantic import BaseModel, ConfigDict, create_model

from openbb_core.app.logs.logging_service import LoggingService
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.abstract.warning import OpenBBWarning, cast_warning
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.metadata import Metadata
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.provider_interface import ExtraParams, ProviderInterface
from openbb_core.app.router import CommandMap
from openbb_core.app.service.system_service import SystemService
from openbb_core.app.service.user_service import UserService
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import maybe_coroutine, run_async


class ExecutionContext:
    """Execution context."""

    def __init__(
        self,
        command_map: CommandMap,
        route: str,
        system_settings: SystemSettings,
        user_settings: UserSettings,
    ) -> None:
        """Initialize the execution context."""
        self.command_map = command_map
        self.route = route
        self.system_settings = system_settings
        self.user_settings = user_settings


class ParametersBuilder:
    """Build parameters for a function."""

    @staticmethod
    def get_polished_parameter_list(func: Callable) -> List[Parameter]:
        """Get the signature parameters values as a list."""
        sig = signature(func)
        parameter_list = list(sig.parameters.values())

        return parameter_list

    @staticmethod
    def get_polished_func(func: Callable) -> Callable:
        """Remove __authenticated_user_settings from the function signature and annotations."""
        func = deepcopy(func)
        sig = signature(func)
        parameter_map = dict(sig.parameters)

        if "__authenticated_user_settings" in parameter_map:
            parameter_map.pop("__authenticated_user_settings")

        parameter_list = list(parameter_map.values())
        new_signature = signature(func).replace(parameters=parameter_list)

        func.__signature__ = new_signature  # type: ignore
        func.__annotations__ = parameter_map

        return func

    @classmethod
    def merge_args_and_kwargs(
        cls,
        func: Callable,
        args: Tuple[Any],
        kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Merge args and kwargs into a single dict."""
        args = deepcopy(args)
        kwargs = deepcopy(kwargs)
        parameter_list = cls.get_polished_parameter_list(func=func)
        parameter_map = {}

        for index, parameter in enumerate(parameter_list):
            if index < len(args):
                parameter_map[parameter.name] = args[index]
            elif parameter.name in kwargs:
                parameter_map[parameter.name] = kwargs[parameter.name]
            elif parameter.default is not parameter.empty:
                parameter_map[parameter.name] = parameter.default
            else:
                parameter_map[parameter.name] = None

        return parameter_map

    @staticmethod
    def update_command_context(
        func: Callable,
        kwargs: Dict[str, Any],
        system_settings: SystemSettings,
        user_settings: UserSettings,
    ) -> Dict[str, Any]:
        """Update the command context with the available user and system settings."""
        argcount = func.__code__.co_argcount
        if "cc" in func.__code__.co_varnames[:argcount]:
            kwargs["cc"] = CommandContext(
                user_settings=user_settings,
                system_settings=system_settings,
            )

        return kwargs

    @staticmethod
    def update_provider_choices(
        func: Callable,
        command_coverage: Dict[str, List[str]],
        route: str,
        kwargs: Dict[str, Any],
        route_default: Optional[Dict[str, Optional[str]]],
    ) -> Dict[str, Any]:
        """Update the provider choices with the available providers and set default provider."""

        def _needs_provider(func: Callable) -> bool:
            """Check if the function needs a provider."""
            parameters = signature(func).parameters.keys()
            return "provider_choices" in parameters

        def _has_provider(kwargs: Dict[str, Any]) -> bool:
            """Check if the kwargs already have a provider."""
            provider_choices = kwargs.get("provider_choices", None)

            if isinstance(provider_choices, dict):  # when in python
                return provider_choices.get("provider", None) is not None
            if isinstance(provider_choices, object):  # when running as fastapi
                return getattr(provider_choices, "provider", None) is not None
            return False

        def _get_first_provider() -> Optional[str]:
            """Get the first available provider."""
            available_providers = ProviderInterface().available_providers
            return available_providers[0] if available_providers else None

        def _get_default_provider(
            command_coverage: Dict[str, List[str]],
            route_default: Optional[Dict[str, Optional[str]]],
        ) -> Optional[str]:
            """
            Get the default provider for the given route.

            Either pick it from the user defaults or from the command coverage.
            """
            cmd_cov_given_route = command_coverage.get(route, None)
            command_cov_provider = (
                cmd_cov_given_route[0] if cmd_cov_given_route else None
            )

            if route_default:
                return route_default.get("provider", None) or command_cov_provider  # type: ignore

            return command_cov_provider

        if not _has_provider(kwargs) and _needs_provider(func):
            provider = (
                _get_default_provider(
                    command_coverage,
                    route_default,
                )
                if route in command_coverage
                else _get_first_provider()
            )
            kwargs["provider_choices"] = {"provider": provider}

        return kwargs

    @staticmethod
    def _warn_kwargs(
        extra_params: Dict[str, Any],
        model: Type[BaseModel],
    ) -> None:
        """Warn if kwargs received and ignored by the validation model."""
        # We only check the extra_params annotation because ignored fields
        # will always be there
        annotation = getattr(
            model.model_fields.get("extra_params", None), "annotation", None
        )
        if is_dataclass(annotation) and any(
            t is ExtraParams for t in getattr(annotation, "__bases__", [])
        ):
            valid = asdict(annotation())  # type: ignore
            for p in extra_params:
                if "chart_params" in p:
                    continue
                if p not in valid:
                    warn(
                        message=f"Parameter '{p}' not found.",
                        category=OpenBBWarning,
                    )

    @staticmethod
    def _as_dict(obj: Any) -> Dict[str, Any]:
        """Safely convert an object to a dict."""
        try:
            if isinstance(obj, dict):
                return obj
            return asdict(obj) if is_dataclass(obj) else dict(obj)
        except Exception:
            return {}

    @staticmethod
    def validate_kwargs(
        func: Callable,
        kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validate kwargs and if possible coerce to the correct type."""
        sig = signature(func)
        fields = {
            n: (
                Any if p.annotation is Parameter.empty else p.annotation,
                ... if p.default is Parameter.empty else p.default,
            )
            for n, p in sig.parameters.items()
        }
        # We allow extra fields to return with model with 'cc: CommandContext'
        config = ConfigDict(extra="allow", arbitrary_types_allowed=True)
        ValidationModel = create_model(func.__name__, __config__=config, **fields)  # type: ignore  # pylint: disable=C0103
        # Validate and coerce
        model = ValidationModel(**kwargs)
        ParametersBuilder._warn_kwargs(
            ParametersBuilder._as_dict(kwargs.get("extra_params", {})),
            ValidationModel,
        )
        return dict(model)

    # pylint: disable=R0913
    @classmethod
    def build(
        cls,
        args: Tuple[Any, ...],
        execution_context: ExecutionContext,
        func: Callable,
        route: str,
        kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build the parameters for a function."""
        func = cls.get_polished_func(func=func)
        system_settings = execution_context.system_settings
        user_settings = execution_context.user_settings
        command_map = execution_context.command_map

        kwargs = cls.merge_args_and_kwargs(
            func=func,
            args=args,
            kwargs=kwargs,
        )
        kwargs = cls.update_command_context(
            func=func,
            kwargs=kwargs,
            system_settings=system_settings,
            user_settings=user_settings,
        )
        kwargs = cls.update_provider_choices(
            func=func,
            command_coverage=command_map.command_coverage,
            route=route,
            kwargs=kwargs,
            route_default=user_settings.defaults.routes.get(route, None),
        )
        kwargs = cls.validate_kwargs(
            func=func,
            kwargs=kwargs,
        )
        return kwargs


# pylint: disable=too-few-public-methods
class StaticCommandRunner:
    """Static Command Runner."""

    @classmethod
    async def _command(
        cls,
        func: Callable,
        kwargs: Dict[str, Any],
        show_warnings: bool = True,  # pylint: disable=unused-argument   # type: ignore
    ) -> OBBject:
        """Run a command and return the output."""
        obbject = await maybe_coroutine(func, **kwargs)
        obbject.provider = getattr(
            kwargs.get("provider_choices", None), "provider", None
        )
        return obbject

    @classmethod
    def _chart(
        cls,
        obbject: OBBject,
        **kwargs,
    ) -> None:
        """Create a chart from the command output."""
        if "charting" not in obbject.accessors:
            raise OpenBBError(
                "Charting is not installed. Please install `openbb-charting`."
            )
        chart_params = {}
        extra_params = kwargs.get("extra_params", {})

        if hasattr(extra_params, "__dict__") and hasattr(extra_params, "chart_params"):
            chart_params = kwargs["extra_params"].__dict__.get("chart_params", {})
        elif isinstance(extra_params, dict) and "chart_params" in extra_params:
            chart_params = kwargs["extra_params"].get("chart_params", {})

        if "chart_params" in kwargs and kwargs["chart_params"] is not None:
            chart_params.update(kwargs.pop("chart_params", {}))

        if (
            "kwargs" in kwargs
            and "chart_params" in kwargs["kwargs"]
            and kwargs["kwargs"].get("chart_params") is not None
        ):
            chart_params.update(kwargs.pop("kwargs", {}).get("chart_params", {}))

        if chart_params:
            kwargs.update(chart_params)
        obbject.charting.show(render=False, **kwargs)

    # pylint: disable=R0913, R0914
    @classmethod
    async def _execute_func(
        cls,
        route: str,
        args: Tuple[Any, ...],
        execution_context: ExecutionContext,
        func: Callable,
        kwargs: Dict[str, Any],
    ) -> OBBject:
        """Execute a function and return the output."""
        user_settings = execution_context.user_settings
        system_settings = execution_context.system_settings

        with catch_warnings(record=True) as warning_list:
            # If we're on Jupyter we need to pop here because we will lose "chart" after
            # ParametersBuilder.build. This needs to be fixed in a way that chart is
            # added to the function signature and shared for jupyter and api
            # We can check in the router decorator if the given function has a chart
            # in the charting extension then we add it there. This way we can remove
            # the chart parameter from the commands.py and package_builder, it will be
            # added to the function signature in the router decorator
            chart = kwargs.pop("chart", False)

            kwargs = ParametersBuilder.build(
                args=args,
                execution_context=execution_context,
                func=func,
                route=route,
                kwargs=kwargs,
            )

            # If we're on the api we need to remove "chart" here because the parameter is added on
            # commands.py and the function signature does not expect "chart"
            kwargs.pop("chart", None)
            # We also pop custom headers
            model_headers = system_settings.api_settings.custom_headers or {}
            custom_headers = {
                name: kwargs.pop(name.replace("-", "_"), default)
                for name, default in model_headers.items() or {}
            } or None

            try:
                obbject = await cls._command(func, kwargs)
                # pylint: disable=protected-access
                obbject._route = route
                obbject._standard_params = kwargs.get("standard_params", None)
                if chart and obbject.results:
                    cls._chart(obbject, **kwargs)

            except Exception as e:
                raise OpenBBError(e) from e
            finally:
                ls = LoggingService(system_settings, user_settings)
                ls.log(
                    user_settings=user_settings,
                    system_settings=system_settings,
                    route=route,
                    func=func,
                    kwargs=kwargs,
                    exec_info=exc_info(),
                    custom_headers=custom_headers,
                )

        if warning_list:
            obbject.warnings = []
            for w in warning_list:
                obbject.warnings.append(cast_warning(w))
                if user_settings.preferences.show_warnings:
                    showwarning(
                        message=w.message,
                        category=w.category,
                        filename=w.filename,
                        lineno=w.lineno,
                        file=w.file,
                        line=w.line,
                    )
        return obbject

    # pylint: disable=W0718
    @classmethod
    async def run(
        cls,
        execution_context: ExecutionContext,
        /,
        *args,
        **kwargs,
    ) -> OBBject:
        """Run a command and return the OBBject as output."""
        timestamp = datetime.now()
        start_ns = perf_counter_ns()

        command_map = execution_context.command_map
        route = execution_context.route

        if func := command_map.get_command(route=route):
            obbject = await cls._execute_func(
                route=route,
                args=args,  # type: ignore
                execution_context=execution_context,
                func=func,
                kwargs=kwargs,
            )
        else:
            raise AttributeError(f"Invalid command : route={route}")

        duration = perf_counter_ns() - start_ns

        if execution_context.user_settings.preferences.metadata:
            try:
                obbject.extra["metadata"] = Metadata(
                    arguments=kwargs,
                    duration=duration,
                    route=route,
                    timestamp=timestamp,
                )
            except Exception as e:
                if Env().DEBUG_MODE:
                    raise OpenBBError(e) from e

        return obbject


class CommandRunner:
    """Command runner."""

    def __init__(
        self,
        command_map: Optional[CommandMap] = None,
        system_settings: Optional[SystemSettings] = None,
        user_settings: Optional[UserSettings] = None,
    ) -> None:
        """Initialize the command runner."""
        self._command_map = command_map or CommandMap()
        self._system_settings = system_settings or SystemService().system_settings
        self._user_settings = user_settings or UserService.read_default_user_settings()

    def init_logging_service(self) -> None:
        """Initialize the logging service."""
        _ = LoggingService(
            system_settings=self._system_settings, user_settings=self._user_settings
        )

    @property
    def command_map(self) -> CommandMap:
        """Command map."""
        return self._command_map

    @property
    def system_settings(self) -> SystemSettings:
        """System settings."""
        return self._system_settings

    @property
    def user_settings(self) -> UserSettings:
        """User settings."""
        return self._user_settings

    @user_settings.setter
    def user_settings(self, user_settings: UserSettings) -> None:
        self._user_settings = user_settings

    # pylint: disable=W1113
    async def run(
        self,
        route: str,
        user_settings: Optional[UserSettings] = None,
        /,
        *args,
        **kwargs,
    ) -> OBBject:
        """Run a command and return the OBBject as output."""
        self._user_settings = user_settings or self._user_settings

        execution_context = ExecutionContext(
            command_map=self._command_map,
            route=route,
            system_settings=self._system_settings,
            user_settings=self._user_settings,
        )

        return await StaticCommandRunner.run(execution_context, *args, **kwargs)

    # pylint: disable=W1113
    def sync_run(
        self,
        route: str,
        user_settings: Optional[UserSettings] = None,
        /,
        *args,
        **kwargs,
    ) -> OBBject:
        """Run a command and return the OBBject as output."""
        return run_async(self.run, route, user_settings, *args, **kwargs)
