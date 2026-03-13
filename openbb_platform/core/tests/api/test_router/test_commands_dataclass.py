"""Test dataclass to dict conversion in API wrapper.

This module tests the fix for the bug where dataclass params (ExtraParams, StandardParams)
do not support item assignment, causing a TypeError when user defaults are applied in the API wrapper.

Bug reproduction:
    File "openbb_platform/core/openbb_core/app/command_runner.py", line 388, in _execute_func
        kwargs_copy["extra_params"][k] = kwargs_copy.pop(
    TypeError: 'FuturesCurve' object does not support item assignment

The fix moves the conversion of dataclass to dict outside and before the defaults block
in commands.py wrapper function.
"""

# pylint: disable=W0612,W0613
# flake8: noqa F401

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from openbb_core.api.router.commands import build_api_wrapper
from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import ExtraParams, StandardParams


@dataclass
class MockStandardParams(StandardParams):
    """Mock standard params with typical fields."""

    symbol: str = "AAPL"
    start_date: str | None = None
    end_date: str | None = None


@dataclass
class MockExtraParams(ExtraParams):
    """Mock extra params with typical fields - NOTE: chart_params is defined here."""

    limit: int | None = None
    chart_params: dict | None = None


@dataclass
class MockExtraParamsWithoutChartParams(ExtraParams):
    """Mock extra params WITHOUT chart_params field.

    This is used to test that defaults can add keys that don't exist in the original
    dataclass - a key scenario for the bug fix.
    """

    limit: int | None = None


class TestAPIWrapperDataclassConversion:
    """Test the actual build_api_wrapper function with dataclass params."""

    @pytest.fixture
    def mock_command_runner(self):
        """Create a mock CommandRunner that captures kwargs passed to run()."""
        runner = MagicMock(spec=CommandRunner)
        captured = {"kwargs": None}

        async def capturing_run(path, user_settings, *args, **kwargs):
            captured["kwargs"] = kwargs  # type: ignore
            return OBBject(results=[{"test": "data"}])

        runner.run = capturing_run
        runner.captured = captured
        return runner

    @pytest.fixture
    def test_route(self):
        """Create a test APIRoute."""

        async def test_endpoint(
            symbol: str = "AAPL",
            standard_params: StandardParams | None = None,
            extra_params: ExtraParams | None = None,
            chart: bool = False,
            **kwargs,
        ):
            return OBBject(results=[{"symbol": symbol}])

        return APIRoute(
            path="/api/v1/test/endpoint",
            endpoint=test_endpoint,
            methods=["GET"],
        )

    def test_wrapper_with_dataclass_params_empty_defaults_chart_true(
        self,
        mock_command_runner,
        test_route,
    ):
        """Test the BUG SCENARIO: dataclass params with empty defaults and chart=True.

        This is the exact scenario that caused the TypeError:
        - standard_params and extra_params are dataclass instances
        - user has no defaults configured (defaults={})
        - chart=True is passed

        The OLD buggy code only converted dataclass to dict inside 'if defaults:',
        so with empty defaults, params remained as dataclass and caused TypeError
        when downstream code tried item assignment.
        """
        wrapper = build_api_wrapper(mock_command_runner, test_route)

        # Create REAL dataclass instances
        standard_params = MockStandardParams(symbol="AAPL")
        extra_params = MockExtraParams(limit=100)

        # Verify these are actual dataclasses that don't support item assignment
        with pytest.raises(TypeError, match="does not support item assignment"):
            standard_params["symbol"] = "TEST"  # type: ignore

        app = FastAPI()
        router = APIRouter()
        router.add_api_route("/api/v1/test/endpoint", wrapper, methods=["GET"])
        app.include_router(router)

        client = TestClient(app, raise_server_exceptions=True)

        # Mock empty defaults (the bug condition)
        with patch(
            "openbb_core.api.router.commands.UserService.read_from_file",
            return_value={},
        ), patch(
            "openbb_core.app.model.user_settings.os.path.exists",
            return_value=False,
        ):
            # Call with chart=True - if bug exists, this raises TypeError
            response = client.get(
                "/api/v1/test/endpoint",
                params={"symbol": "AAPL", "chart": "true"},
            )

        assert response.status_code == 200

        # Verify params were converted to dict
        captured_kwargs = mock_command_runner.captured["kwargs"]
        assert isinstance(captured_kwargs.get("standard_params"), dict)
        assert isinstance(captured_kwargs.get("extra_params"), dict)

    def test_wrapper_with_dataclass_params_with_defaults(
        self,
        mock_command_runner,
        test_route,
    ):
        """Test wrapper correctly applies defaults to converted params."""
        wrapper = build_api_wrapper(mock_command_runner, test_route)
        app = FastAPI()
        router = APIRouter()
        router.add_api_route("/api/v1/test/endpoint", wrapper, methods=["GET"])
        app.include_router(router)
        client = TestClient(app, raise_server_exceptions=True)
        # Mock user settings with defaults
        mock_user_settings_dict = {
            "defaults": {
                "commands": {
                    "api.v1.test.endpoint": {
                        "chart": True,
                        "chart_params": {"title": "Test Chart"},
                    }
                }
            }
        }

        with patch(
            "openbb_core.api.router.commands.UserService.read_from_file",
            return_value=mock_user_settings_dict,
        ), patch(
            "openbb_core.app.model.user_settings.os.path.exists",
            return_value=False,
        ):
            response = client.get(
                "/api/v1/test/endpoint",
                params={"symbol": "MSFT"},
            )

        assert response.status_code == 200

        # Verify defaults were applied
        captured_kwargs = mock_command_runner.captured["kwargs"]
        extra_params = captured_kwargs.get("extra_params", {})

        assert isinstance(extra_params, dict)
        assert extra_params.get("chart_params") == {"title": "Test Chart"}

    def test_wrapper_assigns_chart_params_not_defined_in_dataclass(
        self,
        mock_command_runner,
        test_route,
    ):
        """Test that chart_params can be assigned even when NOT defined in dataclass.

        The bug would cause: TypeError: 'MockExtraParamsWithoutChartParams' object
        does not support item assignment
        """
        wrapper = build_api_wrapper(mock_command_runner, test_route)

        # Create dataclass WITHOUT chart_params field
        extra_params = MockExtraParamsWithoutChartParams(limit=50)

        # Verify chart_params is NOT a field in this dataclass
        assert not hasattr(extra_params, "chart_params")

        # Verify we can't assign to it as a dataclass
        with pytest.raises(TypeError, match="does not support item assignment"):
            extra_params["chart_params"] = {"title": "Test"}  # type: ignore

        app = FastAPI()
        router = APIRouter()
        router.add_api_route("/api/v1/test/endpoint", wrapper, methods=["GET"])
        app.include_router(router)
        client = TestClient(app, raise_server_exceptions=True)
        # Defaults include chart_params which is NOT in the dataclass
        mock_user_settings_dict = {
            "defaults": {
                "commands": {
                    "api.v1.test.endpoint": {
                        "chart_params": {"title": "Added via defaults"},
                    }
                }
            }
        }

        with patch(
            "openbb_core.api.router.commands.UserService.read_from_file",
            return_value=mock_user_settings_dict,
        ), patch(
            "openbb_core.app.model.user_settings.os.path.exists",
            return_value=False,
        ):
            # This should NOT raise TypeError - the fix converts to dict first
            response = client.get(
                "/api/v1/test/endpoint",
                params={"symbol": "AAPL"},
            )

        assert response.status_code == 200

        # Verify chart_params was successfully added to the dict
        captured_kwargs = mock_command_runner.captured["kwargs"]
        extra_params_result = captured_kwargs.get("extra_params", {})

        assert isinstance(extra_params_result, dict)
        # This is the key assertion: chart_params was added even though
        # it wasn't defined in the original dataclass
        assert extra_params_result.get("chart_params") == {
            "title": "Added via defaults"
        }

    def test_wrapper_with_none_params(
        self,
        mock_command_runner,
        test_route,
    ):
        """Test wrapper handles None params gracefully."""
        wrapper = build_api_wrapper(mock_command_runner, test_route)
        app = FastAPI()
        router = APIRouter()
        router.add_api_route("/api/v1/test/endpoint", wrapper, methods=["GET"])
        app.include_router(router)
        client = TestClient(app, raise_server_exceptions=True)

        with patch(
            "openbb_core.api.router.commands.UserService.read_from_file",
            return_value={},
        ), patch(
            "openbb_core.app.model.user_settings.os.path.exists",
            return_value=False,
        ):
            response = client.get(
                "/api/v1/test/endpoint",
                params={"symbol": "AAPL", "chart": "true"},
            )

        assert response.status_code == 200

        # Verify None was converted to empty dict
        captured_kwargs = mock_command_runner.captured["kwargs"]
        assert isinstance(captured_kwargs.get("standard_params"), dict)
        assert isinstance(captured_kwargs.get("extra_params"), dict)

    @pytest.mark.parametrize(
        "has_defaults,chart_value",
        [
            pytest.param(False, False, id="no_defaults_no_chart"),
            pytest.param(False, True, id="no_defaults_chart_true"),
            pytest.param(True, False, id="with_defaults_no_chart"),
            pytest.param(True, True, id="with_defaults_chart_true"),
        ],
    )
    def test_wrapper_all_defaults_chart_combinations(
        self,
        mock_command_runner,
        test_route,
        has_defaults: bool,
        chart_value: bool,
    ):
        """Test all combinations of defaults and chart values."""
        wrapper = build_api_wrapper(mock_command_runner, test_route)
        app = FastAPI()
        router = APIRouter()
        router.add_api_route("/api/v1/test/endpoint", wrapper, methods=["GET"])
        app.include_router(router)
        client = TestClient(app, raise_server_exceptions=True)

        if has_defaults:
            mock_settings = {
                "defaults": {"commands": {"api.v1.test.endpoint": {"limit": 100}}}
            }
        else:
            mock_settings = {}

        with patch(
            "openbb_core.api.router.commands.UserService.read_from_file",
            return_value=mock_settings,
        ), patch(
            "openbb_core.app.model.user_settings.os.path.exists",
            return_value=False,
        ):
            response = client.get(
                "/api/v1/test/endpoint",
                params={"symbol": "AAPL", "chart": str(chart_value).lower()},
            )

        assert response.status_code == 200

        # Params should always be dicts
        captured_kwargs = mock_command_runner.captured["kwargs"]
        assert isinstance(captured_kwargs.get("standard_params"), dict)
        assert isinstance(captured_kwargs.get("extra_params"), dict)


class TestDataclassItemAssignmentBehavior:
    """Tests proving the underlying dataclass behavior that causes the bug."""

    def test_dataclass_does_not_support_item_assignment(self):
        """Prove that dataclass instances raise TypeError on bracket assignment."""
        params = MockExtraParams(limit=10)

        with pytest.raises(TypeError, match="does not support item assignment"):
            params["limit"] = 20  # type: ignore

    def test_dataclass_without_field_does_not_support_new_key_assignment(self):
        """Prove we can't add new keys to a dataclass via item assignment."""
        params = MockExtraParamsWithoutChartParams(limit=10)

        # chart_params is not a field
        assert not hasattr(params, "chart_params")

        with pytest.raises(TypeError, match="does not support item assignment"):
            params["chart_params"] = {"title": "Test"}  # type: ignore

    def test_getattr_dict_converts_to_mutable_dict(self):
        """Verify the fix pattern converts dataclass to mutable dict."""
        params = MockExtraParams(limit=10, chart_params={"title": "Test"})
        # This is the exact pattern used in the fix
        converted = getattr(params, "__dict__", {})

        assert isinstance(converted, dict)

        # Now item assignment works
        converted["limit"] = 20
        converted["new_field"] = "new_value"

        assert converted["limit"] == 20
        assert converted["new_field"] == "new_value"

    def test_getattr_dict_allows_adding_undefined_keys(self):
        """Verify converted dict allows adding keys not in original dataclass."""
        params = MockExtraParamsWithoutChartParams(limit=10)
        converted = getattr(params, "__dict__", {})
        # Now we can add chart_params even though it wasn't a field
        converted["chart_params"] = {"title": "Added after conversion"}

        assert converted["chart_params"] == {"title": "Added after conversion"}

    def test_none_converts_to_empty_dict(self):
        """Verify None gracefully converts to empty dict."""
        none_params = None

        converted = getattr(none_params, "__dict__", {})

        assert converted == {}  # pylint: disable=C1803
        assert isinstance(converted, dict)
