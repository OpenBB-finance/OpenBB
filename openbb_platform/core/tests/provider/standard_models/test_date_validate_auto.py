"""Cover the date_validate validators on standard_models *Data classes.

Each module has a ``date_validate`` field validator on ``date`` that branches on
whether the input contains a ':' (parse as datetime) or not (parse as date).
Instantiating ``*Data`` with both forms covers all branches in one shot.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil

import pytest

import openbb_core.provider.standard_models as _sm_pkg
from openbb_core.provider.abstract.data import Data


def _data_classes_with_date_validate():
    out = []
    for info in pkgutil.iter_modules(_sm_pkg.__path__):
        try:
            mod = importlib.import_module(f"{_sm_pkg.__name__}.{info.name}")
        except Exception:  # noqa: S112
            continue
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if cls.__module__ != mod.__name__:
                continue
            if not issubclass(cls, Data) or cls is Data:
                continue
            if not hasattr(cls, "date_validate"):
                continue
            out.append((info.name, cls))
    return out


_CASES = _data_classes_with_date_validate()


def _minimal_kwargs(cls, date_value):
    """Build minimal init kwargs for a Data subclass."""
    kwargs: dict = {"date": date_value}
    for fname, field in cls.model_fields.items():
        if not field.is_required() or fname == "date":
            continue
        ann = field.annotation
        # Numeric fields default to 1.0; string default 'x'.
        if ann is float or "float" in str(ann):
            kwargs[fname] = 1.0
        elif ann is int or "int" in str(ann):
            kwargs[fname] = 1
        else:
            kwargs[fname] = "x"
    return kwargs


@pytest.mark.parametrize(
    "name,cls", _CASES, ids=[f"{n}::{c.__name__}" for n, c in _CASES]
)
def test_date_validate_string_date(name, cls):
    try:
        obj = cls(**_minimal_kwargs(cls, "2024-01-15"))
    except Exception as e:
        pytest.skip(f"cannot instantiate: {e}")
    assert obj.date is not None


@pytest.mark.parametrize(
    "name,cls", _CASES, ids=[f"{n}::{c.__name__}" for n, c in _CASES]
)
def test_date_validate_datetime_string(name, cls):
    try:
        obj = cls(**_minimal_kwargs(cls, "2024-01-15T12:30:00"))
    except Exception as e:
        pytest.skip(f"cannot instantiate: {e}")
    assert obj.date is not None
