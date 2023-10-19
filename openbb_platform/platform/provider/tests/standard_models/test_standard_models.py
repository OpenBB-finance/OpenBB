"""Test the standard models."""
# pylint: disable=W0401

import inspect
from importlib import import_module
from pathlib import Path

import pytest
from openbb_provider.abstract.fetcher import Data, QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS
from pydantic.fields import FieldInfo

models_path = (
    Path(__file__).parent.parent.parent / "openbb_provider" / "standard_models"
).resolve()
model_files = models_path.glob("*.py")

standard_models = []
for model_file in model_files:
    if model_file.stem == "__init__":
        continue

    model_module = import_module(f"openbb_provider.standard_models.{model_file.stem}")

    for _, obj in inspect.getmembers(model_module):
        if inspect.isclass(obj) and (
            issubclass(obj, Data) or issubclass(obj, QueryParams)
        ):
            if "abstract" in obj.__module__:
                continue
            standard_models.append(obj)


@pytest.mark.parametrize("standard_model", standard_models)
def test_standard_models(standard_model):
    """Test the standard models."""
    assert issubclass(standard_model, Data) or issubclass(
        standard_model, QueryParams
    ), f"{standard_model.__name__} should be a subclass of Data or QueryParams"

    fields = standard_model.model_fields

    for name, field in fields.items():
        assert isinstance(
            field, FieldInfo
        ), f"Field {name} should be a ModelField instance"
        if "QueryParams" in standard_model.__name__:
            if name in QUERY_DESCRIPTIONS:
                assert field.description == QUERY_DESCRIPTIONS[name], (
                    f"Description for {name} is incorrect for the {standard_model.__name__}.\n"
                    f"Please modify or change the field name to a non-reserved name."
                )
        elif name in DATA_DESCRIPTIONS:
            assert field.description == DATA_DESCRIPTIONS[name], (
                f"Description for {name} is incorrect for the {standard_model.__name__}.\n"
                f"Please modify or change the field name to a non-reserved name."
            )
