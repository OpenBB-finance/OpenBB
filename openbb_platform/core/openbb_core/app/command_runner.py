"""Command runner module."""

# pylint: disable=R0903

from copy import deepcopy
from dataclasses import asdict, is_dataclass
from datetime import datetime
from inspect import Parameter, signature
from sys import exc_info
from time import perf_counter_ns
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type
from warnings import catch_warnings, showwarning, warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.abstract.warning import OpenBBWarning, cast_warning
from openbb_core.app.model.metadata import Metadata
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import ExtraParams
from openbb_core.app.static.package_builder import PathHandler
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import maybe_coroutine, run_async
from pydantic import BaseModel, ConfigDict, create_model

if TYPE_CHECKING:
    from fastapi.routing import APIRoute
    from openbb_core.app.model.system_settings import SystemSettings
    from openbb_core.app.model.user_settings import UserSettings
    from openbb_core.app.router import CommandMap


class ExecutionContext:
    """Execution context."""

    # For checking if the command specifies no validation in the API Route
    _route_map = PathHandler.build_route_map()

    def __init__(
        self,
        command_map: "CommandMap",
        route: str,
        system_settings: "SystemSettings",
        user_settings: "UserSettings",
    ) -> None:
        """Initialize the execution context."""
        self.command_map = command_map
        self.route = route
        self.system_settings = system_settings
        self.user_settings = user_settings

    @property
    def api_route(self) -> "APIRoute":
        """API route."""
        return self._route_map[self.route]


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
        args: Tuple[Any, ...],
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
        system_settings: "SystemSettings",
        user_settings: "UserSettings",
    ) -> Dict[str, Any]:
        """Update the command context with the available user and system settings."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.command_context import CommandContext

        argcount = func.__code__.co_argcount
        if "cc" in func.__code__.co_varnames[:argcount]:
            kwargs["cc"] = CommandContext(
                user_settings=user_settings,
                system_settings=system_settings,
            )

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
            return asdict(obj) if is_dataclass(obj) else dict(obj)  # type: ignore
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
        # pylint: disable=C0103
        ValidationModel = create_model(func.__name__, __config__=config, **fields)  # type: ignore
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
        kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build the parameters for a function."""
        func = cls.get_polished_func(func=func)
        system_settings = execution_context.system_settings
        user_settings = execution_context.user_settings

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
        if isinstance(obbject, OBBject):
            obbject.provider = getattr(
                kwargs.get("provider_choices"),
                "provider",
                getattr(obbject, "provider", None),
            )
        return obbject

    @classmethod
    def _chart(
        cls,
        obbject: OBBject,
        **kwargs,
    ) -> None:
        """Create a chart from the command output."""
        try:
            if "charting" not in obbject.accessors:
                raise OpenBBError(
                    "Charting is not installed. Please install `openbb-charting`."
                )
            # Here we will pop the chart_params kwargs and flatten them into the kwargs.
            chart_params = {}
            extra_params = getattr(obbject, "_extra_params", {})

            if extra_params and "chart_params" in extra_params:
                chart_params = extra_params.get("chart_params", {})

            if kwargs.get("chart_params"):
                chart_params.update(kwargs.pop("chart_params", {}))
            # Verify that kwargs is not nested as kwargs so we don't miss any chart params.
            if (
                "kwargs" in kwargs
                and "chart_params" in kwargs["kwargs"]
                and kwargs["kwargs"].get("chart_params")
            ):
                chart_params.update(kwargs.pop("kwargs", {}).get("chart_params", {}))

            if chart_params:
                kwargs.update(chart_params)
            obbject.charting.show(render=False, **kwargs)  # type: ignore[attr-defined]
        except Exception as e:  # pylint: disable=broad-exception-caught
            if Env().DEBUG_MODE:
                raise OpenBBError(e) from e
            warn(str(e), OpenBBWarning)

    @classmethod
    def _extract_params(cls, kwargs, key) -> Dict:
        """Extract params models from kwargs and convert to a dictionary."""
        params = kwargs.get(key, {})
        if hasattr(params, "__dict__"):
            return params.__dict__
        return params

    # pylint: disable=R0913, R0914
    @classmethod
    async def _execute_func(  # pylint: disable=too-many-positional-arguments
        cls,
        route: str,
        args: Tuple[Any, ...],
        execution_context: ExecutionContext,
        func: Callable,
        kwargs: Dict[str, Any],
    ) -> OBBject:
        """Execute a function and return the output."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.logs.logging_service import LoggingService

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

            validate = not execution_context.api_route.openapi_extra.get("no_validate")
            try:
                obbject = await cls._command(func, kwargs)
                # The output might be from a router command with 'no_validate=True'
                # It might be of a different type than OBBject.
                # In this case, we avoid accessing those attributes.
                if isinstance(obbject, OBBject) or validate:
                    if validate and not isinstance(obbject, OBBject):
                        raise OpenBBError(
                            TypeError(
                                f"Expected OBBject instance at function output, got {type(obbject)} instead."
                            )
                        )
                    # This section prepares the obbject to pass to the charting service.
                    obbject._route = route  # pylint: disable=protected-access
                    std_params = cls._extract_params(kwargs, "standard_params") or (
                        kwargs if "data" in kwargs else {}
                    )
                    extra_params = cls._extract_params(kwargs, "extra_params")
                    obbject._standard_params = (  # pylint: disable=protected-access
                        std_params
                    )
                    obbject._extra_params = (  # pylint: disable=protected-access
                        extra_params
                    )
                    if chart and obbject.results:
                        cls._chart(obbject, **kwargs)

                if warning_list:
                    if isinstance(obbject, OBBject):
                        obbject.warnings = []
                    for w in warning_list:
                        if isinstance(obbject, OBBject):
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

        if execution_context.user_settings.preferences.metadata and isinstance(
            obbject, OBBject
        ):
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
                warn(str(e), OpenBBWarning)

        return obbject


class CommandRunner:
    """Command runner."""

    def __init__(
        self,
        command_map: Optional["CommandMap"] = None,
        system_settings: Optional["SystemSettings"] = None,
        user_settings: Optional["UserSettings"] = None,
    ) -> None:
        """Initialize the command runner."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.router import CommandMap
        from openbb_core.app.service.system_service import SystemService
        from openbb_core.app.service.user_service import UserService

        self._command_map = command_map or CommandMap()
        self._system_settings = system_settings or SystemService().system_settings
        self._user_settings = user_settings or UserService.read_from_file()

    def init_logging_service(self) -> None:
        """Initialize the logging service."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.logs.logging_service import LoggingService

        _ = LoggingService(
            system_settings=self._system_settings, user_settings=self._user_settings
        )

    @property
    def command_map(self) -> "CommandMap":
        """Command map."""
        return self._command_map

    @property
    def system_settings(self) -> "SystemSettings":
        """System settings."""
        return self._system_settings

    @property
    def user_settings(self) -> "UserSettings":
        """User settings."""
        return self._user_settings

    @user_settings.setter
    def user_settings(self, user_settings: "UserSettings") -> None:
        self._user_settings = user_settings

    # pylint: disable=W1113
    async def run(
        self,
        route: str,
        user_settings: Optional["UserSettings"] = None,
        /,
        *args,
        **kwargs,
    ) -> OBBject:
        """Run a command and return the OBBject as output."""
        # pylint: disable=import-outside-toplevel

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
        user_settings: Optional["UserSettings"] = None,
        /,
        *args,
        **kwargs,
    ) -> OBBject:
        """Run a command and return the OBBject as output."""
        return run_async(self.run, route, user_settings, *args, **kwargs)
