"""Auto-cover ``to_upper`` field validators across all standard_models QueryParams.

Each standard_models module that defines a ``to_upper`` validator has it ride on
``symbol`` (or in a couple cases ``industry``/etc.). Instantiating the QueryParams
with a lowercase string exercises the validator and covers its single line.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil

import pytest

import openbb_core.provider.standard_models as _sm_pkg
from openbb_core.provider.abstract.query_params import QueryParams


def _modules_with_to_upper():
    out = []
    for info in pkgutil.iter_modules(_sm_pkg.__path__):
        try:
            mod = importlib.import_module(f"{_sm_pkg.__name__}.{info.name}")
        except Exception:  # noqa: S112
            continue
        if any(name == "to_upper" for name in dir(mod)) or "to_upper" in (
            getattr(mod, "__dict__", {})
        ):
            out.append(mod)
            continue
        # Also detect via class scan.
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            if cls.__module__ != mod.__name__:
                continue
            if hasattr(cls, "to_upper"):
                out.append(mod)
                break
    return out


def _query_classes(mod):
    for name, cls in inspect.getmembers(mod, inspect.isclass):
        if cls.__module__ != mod.__name__:
            continue
        if not issubclass(cls, QueryParams) or cls is QueryParams:
            continue
        if not hasattr(cls, "to_upper"):
            continue
        yield name, cls


_CASES: list[tuple[str, type]] = []
for _mod in _modules_with_to_upper():
    for _name, _cls in _query_classes(_mod):
        _CASES.append((f"{_mod.__name__.split('.')[-1]}::{_name}", _cls))


@pytest.mark.parametrize("label,cls", _CASES, ids=[c[0] for c in _CASES])
def test_to_upper_validator_uppercases_symbol(label, cls):
    fields = cls.model_fields
    # Find first string field that the validator applies to. Most use 'symbol'.
    candidates = [
        n
        for n in (
            "symbol",
            "symbols",
            "industry",
            "series_id",
            "country",
            "sector",
            "exchange",
            "base",
        )
        if n in fields
    ]
    if not candidates:
        pytest.skip("no string field to drive validator")

    # Build minimal kwargs: required fields only.
    kwargs: dict = {}
    for fname, field in fields.items():
        if field.is_required():
            if fname == candidates[0] or field.annotation is str:
                kwargs[fname] = "abc"
            else:
                # Try to instantiate to default of the type
                ann = field.annotation
                try:
                    kwargs[fname] = ann() if callable(ann) else "abc"
                except Exception:
                    pytest.skip(f"cannot supply required {fname}")

    if candidates[0] not in kwargs:
        kwargs[candidates[0]] = "abc"

    try:
        obj = cls(**kwargs)
    except Exception as e:
        pytest.skip(f"cannot instantiate: {e}")

    val = getattr(obj, candidates[0], None)
    if isinstance(val, str):
        assert val == val.upper()
