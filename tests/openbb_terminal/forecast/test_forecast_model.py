from typing import Tuple
import pandas as pd
import pytest
from openbb_terminal.forecast import forecast_model as fm
from openbb_terminal.common import common_model
from tests.openbb_terminal.forecast import conftest


@pytest.mark.parametrize("file_type", ["csv", "xlsx", "swp", "juan"])
def test_load(file_type):
    path = conftest.create_path("forecast", "data", f"TSLA.{file_type}")
    common_model.load(file_type, {"TSLA": path})


@pytest.mark.parametrize("name", ["data", None])
def test_get_options(tsla_csv, name):
    val = fm.get_options({"data": tsla_csv}, name)
    assert val["data"].iloc[0]["option"] == "data.date"


@pytest.mark.parametrize(
    "fill, drop",
    [
        (f"{x}fill", f"{y}drop")
        for x in ["r", "c", "rb", "cb", "rf", "cf"]
        for y in ["r", "c"]
    ]
    + [("", "")],
)
def test_clean(tsla_csv, fill, drop):
    val = fm.clean(tsla_csv, fill, drop, 4)
    assert isinstance(val, Tuple)


@pytest.mark.parametrize(
    "command", ["ema", "sto", "rsi", "roc", "momentum", "delta", "atr", "signal"]
)
def test_add_feature_engineering(tsla_csv, command):
    val = getattr(fm, f"add_{command}")(tsla_csv)
    if command == "atr":
        assert isinstance(val, Tuple)
    else:
        assert isinstance(val, pd.DataFrame)


def test_add_sto_bad(capsys):
    fm.add_sto(pd.DataFrame())
    captured = capsys.readouterr()
    assert "Missing" in captured.out


def test_add_atr_bad():
    fm.add_atr(pd.DataFrame())
