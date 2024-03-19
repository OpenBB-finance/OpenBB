import datetime
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Literal, Optional, Union

import pytest
from pydantic import BaseModel, Field

sys.path.append(str(Path(__file__).resolve().parent.parent))

# pylint: disable=unused-argument,redefined-outer-name,wrong-import-position

from generate_platform_v4_markdown import (  # noqa: E402
    get_field_data_type,
    get_function_params_default_value,
    get_post_method_parameters_info,
    get_post_method_returns_info,
    get_provider_field_params,
    get_provider_parameter_info,
)


# Mock Classes
class MockField:
    def __init__(self, annotation):
        self.annotation = annotation


class MockReturnType:
    def __init__(self):
        self.model_fields = {"results": MockField(annotation="List[str]")}


@dataclass
class MockProvider(BaseModel):
    provider: Literal["provider1", "provider2"] = "provider1"


class MockModel(BaseModel):
    provider: Optional[MockProvider] = Field(default=None)


# Mock Pydantic models to simulate your data structure
class OpenBBQueryParams(BaseModel):
    field1: Optional[int] = Field(default=None, description="A sample integer field")
    date: datetime.date = Field(
        default=None, description="A datetime.date type field (expansion type)"
    )


class OpenBBData(BaseModel):
    field1: Literal["a", "b"] = Field(
        default="a", description="A sample Union field with Literal['a', 'b']"
    )
    field2: Optional[int] = Field(
        default=10,
        description="A field with annotated type",
        gt=0,
    )


class Provider1QueryParams(BaseModel):
    field1: Optional[List[str]] = Field(
        default=None, description="A sample List[str] field"
    )


class EmptyModel(BaseModel):
    pass


@pytest.fixture
def mock_data():
    return {
        "openbb": {
            "QueryParams": {"fields": OpenBBQueryParams().model_fields},
            "Data": {"fields": OpenBBData().model_fields},
        },
        "provider1": {
            "QueryParams": {"fields": Provider1QueryParams().model_fields},
            "Data": {"fields": EmptyModel().model_fields},
        },
    }


@pytest.fixture
def mock_endpoint():
    def endpoint(param1: int, param2: Optional[str] = "default"):
        pass  # Mock endpoint function

    return endpoint


class MockEndpointSetup:
    def __init__(self):
        self.mock_endpoint = self._create_mock_endpoint()

    def _create_mock_endpoint(self):
        def mock_endpoint(provider_choices: Optional[MockProvider] = None):
            return ["result1", "result2"]

        # Simulate annotations with a dataclass model
        mock_endpoint.__annotations__ = {
            "provider_choices": Optional[MockProvider],
            "return": List[str],
        }

        return mock_endpoint


@pytest.fixture
def mock_endpoint_setup():
    return MockEndpointSetup()


# Test Classes
class TestFieldDataType:
    @pytest.mark.parametrize(
        "input_type,expected_output",
        [
            (int, "int"),
            (str, "str"),
            (Optional[int], "int"),
            (Union[int, None], "int"),
        ],
    )
    def test_get_field_data_type(self, input_type, expected_output):
        assert get_field_data_type(input_type) == expected_output


class TestProviderFieldParams:
    def test_get_provider_field_params(self, mock_data, monkeypatch):
        monkeypatch.setattr(
            "generate_platform_v4_markdown.get_field_data_type",
            get_field_data_type,
        )
        # Define expected_result based on mock_data and logic in get_provider_field_params
        expected_result_1 = [
            {
                "name": "field1",
                "type": "int",
                "description": "A sample integer field",
                "default": "None",
                "optional": True,
                "standard": True,
            },
            {
                "name": "date",
                "type": "Union[str, date]",
                "description": "A datetime.date type field (expansion type)",
                "default": "None",
                "optional": True,
                "standard": True,
            },
        ]

        expected_result_2 = [
            {
                "name": "field1",
                "type": "List[str]",
                "description": "A sample List[str] field",
                "default": "None",
                "optional": True,
                "standard": False,
            },
        ]

        expected_result_3 = [
            {
                "name": "field1",
                "type": "Literal['a', 'b']",
                "description": "A sample Union field with Literal['a', 'b']",
                "default": "a",
                "optional": True,
                "standard": True,
            },
            {
                "name": "field2",
                "type": "int",
                "description": "A field with annotated type",
                "default": "10",
                "optional": True,
                "standard": True,
            },
        ]

        result = get_provider_field_params(mock_data, "QueryParams")
        assert result == expected_result_1

        result = get_provider_field_params(mock_data, "QueryParams", "provider1")
        assert result == expected_result_2

        result = get_provider_field_params(mock_data, "Data")
        assert result == expected_result_3


class TestProviderParameterInfo:
    def test_get_provider_parameter_info(self, mock_endpoint_setup):
        # Access the mock_endpoint from the fixture
        mock_endpoint = mock_endpoint_setup.mock_endpoint

        expected = {
            "name": "provider",
            "type": "Literal['provider1', 'provider2']",
            "description": "The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'provider1' if there is no default.",  # noqa: E501
            "default": "provider1",
            "optional": True,
            "standard": True,
        }

        result = get_provider_parameter_info(mock_endpoint)
        assert result == expected


class TestFunctionParamsDefaultValue:
    def test_get_function_params_default_value(self, mock_endpoint):
        expected_result = {
            "param1": "",
            "param2": "default",
        }

        result = get_function_params_default_value(mock_endpoint)
        assert (
            result == expected_result
        ), "Failed to correctly identify default parameter values."


class TestPostMethodParametersInfo:
    def test_get_post_method_parameters_info(self, monkeypatch):
        monkeypatch.setattr(
            "generate_platform_v4_markdown.get_field_data_type",
            get_field_data_type,
        )

        def mock_endpoint(param1: int, param2: Optional[str] = "default"):
            """
            A mock endpoint function.

            Parameters
            ----------
            param1 : int
                The first parameter.
            param2 : Optional[str]
                The second parameter, optional.
            """
            return

        expected_result = [
            {
                "name": "param1",
                "type": "int",
                "description": "The first parameter.",
                "default": "",
                "optional": False,
            },
            {
                "name": "param2",
                "type": "str",
                "description": "The second parameter, optional.",
                "default": "default",
                "optional": True,
            },
        ]

        result = get_post_method_parameters_info(mock_endpoint)
        assert (
            result == expected_result
        ), "Failed to correctly extract POST method parameters info."


class TestPostMethodReturnsInfo:
    def test_get_post_method_returns_info(self, monkeypatch):
        monkeypatch.setattr(
            "generate_platform_v4_markdown.get_field_data_type",
            get_field_data_type,
        )

        class MockReturnModel(BaseModel):
            results: List[str]

        def mock_endpoint() -> MockReturnModel:
            """
            A mock endpoint function.

            Parameters
            ----------
            None

            Returns
            -------
            MockReturnModel
                A list of strings as results.
            """
            return

        expected_result = [
            {
                "name": "results",
                "type": "List[str]",
                "description": "A list of strings as results.",
            }
        ]

        result = get_post_method_returns_info(mock_endpoint)
        assert (
            result == expected_result
        ), "Failed to correctly extract POST method returns info."
