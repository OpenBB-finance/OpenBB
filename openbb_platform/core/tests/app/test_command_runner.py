from inspect import Parameter
from typing import Dict, List
from unittest.mock import patch

import pytest
from openbb_core.app.command_runner import (
    CommandRunner,
    ExecutionContext,
    ParametersBuilder,
    StaticCommandRunner,
)
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.router import CommandMap


@pytest.fixture()
def execution_context():
    """Set up execution context."""
    sys = SystemSettings()
    user = UserSettings()
    cmd_map = CommandMap()
    return ExecutionContext(cmd_map, "mock/route", sys, user)


@pytest.fixture()
def mock_func():
    """Set up mock function."""

    def mock_func(
        a: int, b: int, c: float = 10.0, d: int = 5, provider_choices: Dict = {}
    ) -> None:
        pass

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
    assert polished_func.__signature__ == input_func.__signature__


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
    def other_mock_func(
        cc: CommandContext,
        a: int,
        b: int,
    ) -> None:
        pass

    result = ParametersBuilder.update_command_context(
        other_mock_func, kwargs, system_settings, user_settings
    )

    assert isinstance(result["cc"], CommandContext)
    assert result["cc"].system_settings == system_settings
    assert result["cc"].user_settings == user_settings


@pytest.mark.parametrize(
    "command_coverage, route, kwargs, route_default, expected_result",
    [
        (
            {"route1": ["choice1", "choice2"]},
            "route1",
            {"provider_choices": {"provider": None}},
            None,
            {"provider_choices": {"provider": None}},
        ),
        (
            {"route1": ["choice1", "choice2"]},
            "route1",
            {"provider_choices": {"provider": ["choice1", "choice2"]}},
            {"provider": "choice1"},
            {"provider_choices": {"provider": ["choice1", "choice2"]}},
        ),
        (
            {},
            "route2",
            {},
            {"provider": "default_provider"},
            {},
        ),
        (
            {},
            "route3",
            {"provider_choices": {"provider": "existing_provider"}},
            None,
            {"provider_choices": {"provider": "existing_provider"}},
        ),
    ],
)
def test_parameters_builder_update_provider_choices(
    command_coverage, route, kwargs, route_default, expected_result
):
    with patch(
        "openbb_core.app.command_runner.ProviderInterface",
        **{"return_value.available_providers": ["provider1", "provider2"]},
    ):
        result = ParametersBuilder.update_provider_choices(
            mock_func, command_coverage, route, kwargs, route_default
        )

        assert result == expected_result


def test_parameters_builder_validate_kwargs(mock_func):
    """Test validate_kwargs."""

    # TODO: add more test cases with @pytest.mark.parametrize

    result = ParametersBuilder.validate_kwargs(
        mock_func, {"a": 1, "b": "2", "c": 3.0, "d": 4}
    )

    assert result == {"a": 1, "b": 2, "c": 3.0, "d": 4, "provider_choices": {}}


def test_parameters_builder_build(mock_func, execution_context):
    """Test build."""

    # TODO: add more test cases with @pytest.mark.parametrize

    with patch(
        "openbb_core.app.command_runner.ProviderInterface",
        **{"return_value.available_providers": ["provider1", "provider2"]},
    ):
        result = ParametersBuilder.build(
            args=[1, 2],
            kwargs={
                "c": 3,
                "d": "4",
                "provider_choices": {"provider": ["provider1", "provider2"]},
            },
            func=mock_func,
            execution_context=execution_context,
            route="mock/route",
        )

        assert result == {
            "a": 1,
            "b": 2,
            "c": 3.0,
            "d": 4,
            "provider_choices": {"provider": ["provider1", "provider2"]},
        }


@patch("openbb_core.app.command_runner.LoggingService")
def test_command_runner(_):
    """Test command runner."""

    assert CommandRunner()


@patch("openbb_core.app.command_runner.LoggingService")
def test_command_runner_properties(mock_logging_service):
    """Test properties."""

    sys = SystemSettings()
    user = UserSettings()
    cmd_map = CommandMap()
    runner = CommandRunner(cmd_map, sys, user)

    assert isinstance(runner, CommandRunner)
    assert runner.system_settings == sys
    assert runner.user_settings == user
    assert runner.command_map == cmd_map
    assert mock_logging_service.called_once()


@patch("openbb_core.app.command_runner.LoggingService")
def test_command_runner_run(_):
    runner = CommandRunner()

    with patch(
        "openbb_core.app.command_runner.StaticCommandRunner",
        **{"return_value.run": True},
    ):
        assert runner.run("mock/route")


@pytest.mark.asyncio
@patch("openbb_core.app.command_runner.CommandMap.get_command")
@patch("openbb_core.app.command_runner.StaticCommandRunner._execute_func")
async def test_static_command_runner_run(
    mock_execute_func, mock_get_command, execution_context
):
    """Test static command runner run."""

    def other_mock_func(a: int, b: int, c: int, d: int) -> List[int]:
        return [a, b, c, d]

    class MockOBBject:
        """Mock OBBject"""

        def __init__(self, results):
            self.results = results
            self.extra = {}

    mock_get_command.return_value = other_mock_func
    mock_execute_func.return_value = MockOBBject(results=[1, 2, 3, 4])

    result = await StaticCommandRunner.run(execution_context, 1, 2, c=3, d=4)

    assert result.results == [1, 2, 3, 4]
    assert hasattr(result, "extra")
    assert result.extra.get("metadata") is not None


@pytest.mark.asyncio
@patch("openbb_core.app.command_runner.LoggingService")
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

    class MockOBBject:
        """Mock OBBject"""

        def __init__(self, results):
            self.results = results
            self.extra = {}

    mock_parameters_builder_build.return_value = {
        "a": 1,
        "b": 2,
        "c": 3.0,
        "d": 4,
        "provider_choices": {"provider": ["provider1", "provider2"]},
        "chart": True,
    }
    mock_logging_service.log.return_value = None
    mock_command.return_value = MockOBBject(results=[1, 2, 3, 4])
    mock_chart.return_value = None

    result = await StaticCommandRunner._execute_func(
        "mock/route", (1, 2, 3, 4), execution_context, mock_func, {}
    )

    assert result.results == [1, 2, 3, 4]
    assert mock_logging_service.called_once()
    assert mock_parameters_builder_build.called_once()
    assert mock_command.called_once()
    assert mock_chart.called_once()


@patch("openbb_core.app.command_runner.ChartingService.chart")
def test_static_command_runner_chart(mock_charting_service_chart, execution_context):
    """Test chart."""

    class MockOBBject:
        """Mock OBBject"""

        def __init__(self, results):
            self.results = results
            self.chart = {}

    mock_charting_service_chart.return_value = {"mock": "chart"}
    mock_obbject = MockOBBject(results=[1, 2, 3, 4])

    StaticCommandRunner._chart(
        obbject=mock_obbject,
        user_settings=execution_context.user_settings,
        system_settings=execution_context.system_settings,
        route="mock/route",
    )

    assert mock_charting_service_chart.called_once()
    assert mock_obbject.results == [1, 2, 3, 4]
    assert mock_obbject.chart == {"mock": "chart"}


@pytest.mark.asyncio
async def test_static_command_runner_command():
    """Test command."""

    class MockOBBject:
        """Mock OBBject"""

        def __init__(self, results):
            self.results = results
            self.extra = {}

    class MockProviderChoices:
        """Mock ProviderChoices"""

        def __init__(self, provider):
            self.provider = provider

    def other_mock_func(**kwargs):
        return MockOBBject(results=[1, 2, 3, 4])

    mock_provider_choices = MockProviderChoices(provider="mock_provider")

    result = await StaticCommandRunner._command(
        func=other_mock_func,
        kwargs={"provider_choices": mock_provider_choices},
    )

    assert result.results == [1, 2, 3, 4]
    assert result.provider == "mock_provider"
