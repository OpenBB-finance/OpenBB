"""Test the example_generator.py file."""
# pylint: disable=redefined-outer-name, protected-access


import pytest
from openbb_core.app.example_generator import ExampleGenerator
from pydantic import Field


@pytest.fixture(scope="module")
def example_generator():
    """Return example generator."""
    return ExampleGenerator()


def test_docstring_generator_init(example_generator):
    """Test example generator init."""
    assert example_generator


def test_generate_example(example_generator):
    """Test generate example."""
    route = "test_route.test_subroute"
    standard_params = {"test_param": Field(default="test_value")}
    example = example_generator.generate_example(
        route=route,
        standard_params=standard_params,
    )
    assert example == 'obb.test_route.test_subroute(test_param="test_value")\n'


def test_generate_example_no_route(example_generator):
    """Test generate example no route."""
    route = ""
    standard_params = {"test_param": Field(default="test_value")}
    example = example_generator.generate_example(
        route=route,
        standard_params=standard_params,
    )
    assert example == ""


def test_generate_example_no_params(example_generator):
    """Test generate example no params."""
    route = "test_route.test_subroute"
    standard_params = {}
    example = example_generator.generate_example(
        route=route,
        standard_params=standard_params,
    )
    assert example == "obb.test_route.test_subroute()"


def test_get_model_standard_params(example_generator):
    """Test get model standard params."""
    param_fields = {
        "test_param": Field(default="test_value"),
        "test_param2": Field(default="test_value2"),
    }
    test_params = example_generator.get_model_standard_params(param_fields=param_fields)
    assert test_params == {
        "test_param": "test_value",
        "test_param2": "test_value2",
    }
