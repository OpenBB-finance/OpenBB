"""Test command runner."""

from dataclasses import dataclass
from inspect import Parameter
from typing import Dict, List
from unittest.mock import Mock, patch

import pytest
from fastapi import Query
from fastapi.params import Query as QueryParam
from openbb_core.app.command_runner import (
    CommandRunner,
    ExecutionContext,
    ParametersBuilder,
    StaticCommandRunner,
)
from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.provider_interface import ExtraParams
from openbb_core.app.router import CommandMap
from pydantic import BaseModel, ConfigDict

# pylint: disable=W0613, W0621, W0102, W0212


class MockAPIRoute:
    """MockAPIRoute"""

    def __init__(self, route):
        """Initialize the mock API route."""
        self.route = route
        self.openapi_extra = {"no_validate": True}


class MockExecutionContext:
    """MockExecutionContext"""

    _route_map = {"mock/route": "mock_func"}

    def __init__(self, cmd_map, route, sys, user):
        """Initialize the mock execution context."""
        self.command_map = cmd_map
        self.route = route
        self.system_settings = sys
        self.user_settings = user

    @property
    def api_route(self) -> str:
        """Mock API route."""
        return MockAPIRoute(self.route)


@pytest.fixture()
def execution_context():
    """Set up execution context."""
    sys = SystemSettings()
    user = UserSettings()
    cmd_map = CommandMap()
    return MockExecutionContext(cmd_map, "mock/route", sys, user)


@pytest.fixture()
def mock_func():
    """Set up mock function."""

    def mock_func(
        a: int, b: int, c: float = 10.0, d: int = 5, provider_choices: Dict = {}
    ) -> None:
        """Mock function."""

    return mock_func


def test_execution_context():
    """Test execution context."""
    sys = SystemSettings()
    user = UserSettings()
    cmd_map = CommandMap()
    ctx = ExecutionContext(cmd_map, "mock/route", sys, user)

    assert isinstance(ctx, ExecutionContext)
    assert ctx.system_settings == sys
    assert ctx.user_settings == user
    assert ctx.command_map == cmd_map
    assert ctx.route == "mock/route"


def test_parameters_builder():
    """Test parameters builder."""
    assert ParametersBuilder()


@pytest.mark.parametrize(
    "input_func, expected_annotations",
    [
        (lambda x: x, {"x": Parameter(name="x", kind=Parameter.POSITIONAL_OR_KEYWORD)}),
        (
            lambda a, b, c=10: a + b + c,
            {
                "a": Parameter(name="a", kind=Parameter.POSITIONAL_OR_KEYWORD),
                "b": Parameter(name="b", kind=Parameter.POSITIONAL_OR_KEYWORD),
                "c": Parameter(
                    name="c", kind=Parameter.POSITIONAL_OR_KEYWORD, default=10
                ),
            },
        ),
        (
            lambda x, y, *, z: x + y + z,
            {
                "x": Parameter(name="x", kind=Parameter.POSITIONAL_OR_KEYWORD),
                "y": Parameter(name="y", kind=Parameter.POSITIONAL_OR_KEYWORD),
                "z": Parameter(name="z", kind=Parameter.KEYWORD_ONLY),
            },
        ),
    ],
)
def test_parameters_builder_get_polished_func(input_func, expected_annotations):
    """Test get_polished_func."""
    polished_func = ParametersBuilder.get_polished_func(input_func)

    assert polished_func.__annotations__ == expected_annotations
    assert polished_func.__signature__ == input_func.__signature__  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "input_func, expected_params",
    [
        (lambda x: x, [Parameter("x", Parameter.POSITIONAL_OR_KEYWORD)]),
        (
            lambda a, b, c=10: a + b + c,
            [
                Parameter("a", Parameter.POSITIONAL_OR_KEYWORD),
                Parameter("b", Parameter.POSITIONAL_OR_KEYWORD),
                Parameter("c", Parameter.POSITIONAL_OR_KEYWORD, default=10),
            ],
        ),
        (
            lambda x, y, *, z: x + y + z,
            [
                Parameter("x", Parameter.POSITIONAL_OR_KEYWORD),
                Parameter("y", Parameter.POSITIONAL_OR_KEYWORD),
                Parameter("z", Parameter.KEYWORD_ONLY),
            ],
        ),
    ],
)
def test_parameters_builder_get_polished_parameter_list(input_func, expected_params):
    """Test get_polished_parameter_list."""
    param_list = ParametersBuilder.get_polished_parameter_list(input_func)

    assert param_list == expected_params


@pytest.mark.parametrize(
    "input_func, input_args, input_kwargs, expected_result",
    [
        (lambda x: x, (5,), {}, {"x": 5}),
        (lambda a, b, c=10: a + b + c, (2, 3), {}, {"a": 2, "b": 3, "c": 10}),
        (lambda x, y, *, z: x + y + z, (1, 2), {"z": 3}, {"x": 1, "y": 2, "z": 3}),
    ],
)
def test_parameters_builder_merge_args_and_kwargs(
    input_func, input_args, input_kwargs, expected_result
):
    """Test merge_args_and_kwargs."""
    result = ParametersBuilder.merge_args_and_kwargs(
        input_func, input_args, input_kwargs
    )

    assert result == expected_result


@pytest.mark.parametrize(
    "kwargs, system_settings, user_settings, expected_result",
    [
        (
            {"cc": "existing_cc"},
            SystemSettings(),
            UserSettings(),
            {"cc": "mock_cc"},
        ),
    ],
)
def test_parameters_builder_update_command_context(
    kwargs, system_settings, user_settings, expected_result
):
    """Test update_command_context."""

    def other_mock_func(
        cc: CommandContext,
        a: int,
        b: int,
    ) -> None:
        """Mock function."""

    result = ParametersBuilder.update_command_context(
        other_mock_func, kwargs, system_settings, user_settings
    )

    assert isinstance(result["cc"], CommandContext)
    assert result["cc"].system_settings == system_settings
    assert result["cc"].user_settings == user_settings


def test_parameters_builder_validate_kwargs(mock_func):
    """Test validate_kwargs."""
    # TODO: add more test cases with @pytest.mark.parametrize

    result = ParametersBuilder.validate_kwargs(
        mock_func, {"a": 1, "b": "2", "c": 3.0, "d": 4}
    )

    assert result == {"a": 1, "b": 2, "c": 3.0, "d": 4, "provider_choices": {}}


@pytest.mark.parametrize(
    "extra_params, base, expect",
    [
        (
            {"exists": ...},
            ExtraParams,
            None,
        ),
        (
            {"inexistent_field": ...},
            ExtraParams,
            OpenBBWarning,
        ),
    ],
)
def test_parameters_builder__warn_kwargs(extra_params, base, expect):
    """Test _warn_kwargs."""

    @dataclass
    class SomeModel(base):  # type: ignore[misc,valid-type]
        """SomeModel"""

        exists: QueryParam = Query(...)

    class Model(BaseModel):
        """Model"""

        model_config = ConfigDict(arbitrary_types_allowed=True)
        extra_params: SomeModel

    with pytest.warns(expect) as warning_info:
        # pylint: disable=protected-access
        ParametersBuilder._warn_kwargs(extra_params, Model)

        if not expect:
            assert len(warning_info) == 0


def test_parameters_builder_build(mock_func, execution_context):
    """Test build."""
    # TODO: add more test cases with @pytest.mark.parametrize

    with patch("openbb_core.app.provider_interface.ProviderInterface") as mock_pi:
        mock_pi.available_providers = ["provider1", "provider2"]

        result = ParametersBuilder.build(
            args=(1, 2),
            kwargs={
                "c": 3,
                "d": "4",
                "provider_choices": {"provider": "provider1"},
            },
            func=mock_func,
            execution_context=execution_context,
        )

        assert result == {
            "a": 1,
            "b": 2,
            "c": 3.0,
            "d": 4,
            "provider_choices": {"provider": "provider1"},
        }


def test_command_runner():
    """Test command runner."""
    assert CommandRunner()


def test_command_runner_properties():
    """Test properties."""
    sys = SystemSettings()
    user = UserSettings()
    cmd_map = CommandMap()
    runner = CommandRunner(cmd_map, sys, user)

    assert isinstance(runner, CommandRunner)
    assert runner.system_settings == sys
    assert runner.user_settings == user
    assert runner.command_map == cmd_map


@patch("openbb_core.app.command_runner.CommandRunner")
def test_command_runner_run(_):
    """Test run."""
    runner = CommandRunner()

    with patch(
        "openbb_core.app.command_runner.StaticCommandRunner",
        **{"return_value.run": True},
    ):
        assert runner.run("mock/route")


@pytest.mark.asyncio
@patch("openbb_core.app.router.CommandMap.get_command")
@patch("openbb_core.app.command_runner.StaticCommandRunner._execute_func")
async def test_static_command_runner_run(
    mock_execute_func, mock_get_command, execution_context
):
    """Test static command runner run."""

    def other_mock_func(a: int, b: int, c: int, d: int) -> List[int]:
        """Mock function."""
        return [a, b, c, d]

    class MockOBBject:
        """Mock OBBject"""

        def __init__(self, results):
            """Initialize the mock object."""
            self.results = results
            self.extra = {}
            self.extra["metadata"] = {"test": "test"}
            self.provider = None

    mock_get_command.return_value = other_mock_func
    mock_execute_func.return_value = MockOBBject(results=[1, 2, 3, 4])

    result = await StaticCommandRunner.run(execution_context, 1, 2, c=3, d=4)

    assert result.results == [1, 2, 3, 4]
    assert hasattr(result, "extra")
    assert result.extra.get("metadata") is not None


@pytest.mark.asyncio
@patch("openbb_core.app.logs.logging_service.LoggingService")
@patch("openbb_core.app.command_runner.ParametersBuilder.build")
@patch("openbb_core.app.command_runner.StaticCommandRunner._command")
@patch("openbb_core.app.command_runner.StaticCommandRunner._chart")
async def test_static_command_runner_execute_func(
    mock_chart,
    mock_command,
    mock_parameters_builder_build,
    mock_logging_service,
    execution_context,
    mock_func,
):
    """Test execute_func."""

    static_command_runner = StaticCommandRunner()

    mock_parameters_builder_build.return_value = {
        "a": 1,
        "b": 2,
        "c": 3.0,
        "d": 4,
        "provider_choices": {"provider": ["provider1", "provider2"]},
        "chart": True,
    }
    mock_logging_service.log.return_value = None
    mock_command.return_value = OBBject(
        results=[1, 2, 3, 4],
        provider="mock_provider",
        accessors={"charting": Mock()},
    )
    mock_chart.return_value = None

    result = await static_command_runner._execute_func(
        "mock/route", (1, 2, 3, 4), execution_context, mock_func, {"chart": True}
    )

    assert result.results == [1, 2, 3, 4]
    mock_logging_service.assert_called_once()
    mock_parameters_builder_build.assert_called_once()
    mock_command.assert_called_once()
    mock_chart.assert_called_once()


def test_static_command_runner_chart():
    """Test _chart method when charting is in obbject.accessors."""

    mock_obbject = OBBject(
        results=[
            {"date": "1990", "value": 100},
            {"date": "1991", "value": 200},
            {"date": "1992", "value": 300},
        ],
        provider="mock_provider",
        accessors={"charting": Mock()},
    )
    mock_obbject.charting.show = Mock()

    StaticCommandRunner._chart(mock_obbject)  # pylint: disable=protected-access

    mock_obbject.charting.show.assert_called_once()


@pytest.mark.asyncio
async def test_static_command_runner_command():
    """Test command."""

    class MockOBBject:
        """Mock OBBject"""

        def __init__(self, results, **kwargs):
            self.results = results
            self.extra = {}
            self.provider = kwargs.get("provider_choices").provider

    class MockProviderChoices:
        """Mock ProviderChoices"""

        def __init__(self, provider):
            self.provider = provider

    def other_mock_func(**kwargs):
        return MockOBBject([1, 2, 3, 4], **kwargs)

    mock_provider_choices = MockProviderChoices(provider="mock_provider")

    result = await StaticCommandRunner._command(
        func=other_mock_func,
        kwargs={"provider_choices": mock_provider_choices},
    )

    assert result.results == [1, 2, 3, 4]
    assert result.provider == "mock_provider"
