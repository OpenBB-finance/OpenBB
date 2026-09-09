"""Test API exception handlers."""

import asyncio
import json

import pytest
from fastapi.exceptions import ResponseValidationError
from openbb_core.api.exception_handlers import ExceptionHandlers
from pydantic import BaseModel, ValidationError


class MockQueryParams(BaseModel):
    """Mock query parameters with a required field."""

    category: str


class MockRequestParams(BaseModel):
    """Mock non-query request parameters with a required field."""

    value: str


class MockRequest:
    """Minimal request double with query parameters and an optional body."""

    def __init__(self, body: bytes = b""):
        self.query_params = {}
        self._body = body

    async def body(self) -> bytes:
        """Return the configured request body."""
        return self._body


def get_response_detail(response):
    """Return the JSON response detail."""
    return json.loads(response.body)["detail"]


def test_validation_missing_query_param_returns_422():
    """Return 422 when a fetcher QueryParams field is missing from the query."""
    with pytest.raises(ValidationError) as exc_info:
        MockQueryParams.model_validate({})

    request = MockRequest()
    response = asyncio.run(ExceptionHandlers.validation(request, exc_info.value))

    assert response.status_code == 422
    detail = get_response_detail(response)
    assert detail[0]["loc"] == ["query", "category"]


def test_validation_response_error_returns_422():
    """Keep response validation errors on the 422 path."""
    error = ResponseValidationError(
        [
            {
                "type": "missing",
                "loc": ("response", "value"),
                "msg": "Field required",
                "input": {},
            }
        ]
    )
    request = MockRequest()

    response = asyncio.run(ExceptionHandlers.validation(request, error))

    assert response.status_code == 422
    detail = get_response_detail(response)
    assert detail[0]["loc"] == ["query", "response", "value"]


def test_validation_non_query_params_error_returns_500():
    """Keep non-QueryParams validation errors on the unexpected-error path."""
    with pytest.raises(ValidationError) as exc_info:
        MockRequestParams.model_validate({})

    request = MockRequest(body=b"{}")
    response = asyncio.run(ExceptionHandlers.validation(request, exc_info.value))

    assert response.status_code == 500


def test_validation_query_params_model_bound_to_body_is_not_query_scoped():
    """Do not relabel body-bound QueryParams errors as query parameters."""
    with pytest.raises(ValidationError) as exc_info:
        MockQueryParams.model_validate({})

    response = asyncio.run(ExceptionHandlers.validation(MockRequest(body=b"{}"), exc_info.value))

    assert response.status_code == 500
