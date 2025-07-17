"""App tests for Nasdaq provider."""

# flake8: noqa:E501
# pylint: disable=redefined-outer-name, unused-argument, line-too-long
import json
import os
from pathlib import Path

import pytest
from fastapi import FastAPI
from openbb_nasdaq.app import main
from openbb_platform_api.utils.widgets import build_json


@pytest.fixture(scope="module")
def nasdaq_app():
    """Fixture to serve FastAPI app instance."""
    app = main()
    yield app


@pytest.fixture(scope="module")
def expected_apps():
    """Load expected apps.json data."""
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    with open(current_dir / "record" / "expected_apps.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def expected_widgets():
    """Load expected widgets.json data."""
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    with open(current_dir / "record" / "expected_widgets.json", encoding="utf-8") as f:
        return json.load(f)


def test_app_is_fastapi_instance(nasdaq_app):
    """Test that the factory function returns a FastAPI instance."""
    assert isinstance(nasdaq_app, FastAPI)


def test_app_has_routes(nasdaq_app):
    """Test that the app has at least one route."""
    assert len(nasdaq_app.routes) > 0


@pytest.mark.asyncio
async def test_apps_json(nasdaq_app, expected_apps):
    """Test the /apps.json endpoint. This looks for changes and verifies the endpoint works."""
    route = [d for d in nasdaq_app.routes if d.path == "/apps.json"][0]
    response = await route.endpoint()
    assert isinstance(response, dict)
    assert response == expected_apps


def test_widgets_json(nasdaq_app, expected_widgets):
    """Test the /widgets.json endpoint. This looks for changes and verifies that the widgets are being generated correctly."""
    openapi_json: dict = nasdaq_app.openapi()
    assert isinstance(openapi_json, dict)
    response = build_json(openapi_json, [])
    assert isinstance(response, dict)
    assert response == expected_widgets
