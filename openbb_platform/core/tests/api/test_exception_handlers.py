"""Tests for API exception handlers."""

import asyncio

from fastapi import Request
from openbb_core.api.exception_handlers import ExceptionHandlers
from pydantic import BaseModel, ValidationError


class RequiredQueryParams(BaseModel):
    """Query parameters used to exercise fetcher-side validation."""

    category: str


def test_missing_fetcher_query_param_returns_422():
    """Missing required fields from QueryParams are request validation errors."""
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/api/v1/economy/survey/bls_search",
            "headers": [],
            "query_string": b"",
        }
    )

    try:
        RequiredQueryParams()
    except ValidationError as error:
        response = asyncio.run(ExceptionHandlers.validation(request, error))
    else:
        raise AssertionError("RequiredQueryParams should require category")

    assert response.status_code == 422
    assert b'"loc":["query","category"]' in response.body
