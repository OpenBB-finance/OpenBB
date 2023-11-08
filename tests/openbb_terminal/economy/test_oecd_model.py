from datetime import datetime

import pandas as pd
import pytest

from openbb_terminal.economy import oecd_model


@pytest.mark.vcr
def test_get_gdp(recorder):
    """Test get_gdp"""
    data = oecd_model.get_gdp(
        countries=["united_states", "canada"],
        start_date="2020-01-01",
        end_date="2022-01-31",
    )
    assert isinstance(data, pd.DataFrame)
    recorder.capture(data)


@pytest.mark.vcr
def test_get_rgdp(recorder):
    """Test get_real_gdp"""
    data = oecd_model.get_real_gdp(
        countries=["united_states", "canada"],
        start_date=datetime.strptime("2020-01-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2022-01-31", "%Y-%m-%d"),
    )
    assert isinstance(data, pd.DataFrame)
    recorder.capture(data)


@pytest.mark.vcr
def test_get_fgdp(recorder):
    """Test get_gdp_forecast"""
    data = oecd_model.get_gdp_forecast(
        countries=["united_states", "canada"],
        start_date=datetime.strptime("2020-01-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2022-01-31", "%Y-%m-%d"),
    )
    assert isinstance(data, pd.DataFrame)
    recorder.capture(data)


@pytest.mark.vcr
def test_get_debt(recorder):
    """Test get_debt"""
    data = oecd_model.get_debt(
        countries=["united_states", "canada"],
        start_date=datetime.strptime("2020-01-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2022-01-31", "%Y-%m-%d"),
    )
    assert isinstance(data, pd.DataFrame)
    recorder.capture(data)


@pytest.mark.vcr
def test_get_cpi(recorder):
    """Test get_cpi"""
    data = oecd_model.get_cpi(
        countries=["united_states", "canada"],
        start_date=datetime.strptime("2020-01-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2022-01-31", "%Y-%m-%d"),
    )
    assert isinstance(data, pd.DataFrame)
    recorder.capture(data)


@pytest.mark.vcr
def test_get_balance(recorder):
    """Test get_balance"""
    data = oecd_model.get_balance(
        countries=["united_states", "canada"],
        start_date=datetime.strptime("2020-01-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2022-01-31", "%Y-%m-%d"),
    )
    assert isinstance(data, pd.DataFrame)
    recorder.capture(data)


@pytest.mark.vcr
def test_get_revenue(recorder):
    """Test get_revenue"""
    data = oecd_model.get_revenue(
        countries=["united_states", "canada"],
        start_date=datetime.strptime("2020-01-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2022-01-31", "%Y-%m-%d"),
    )
    assert isinstance(data, pd.DataFrame)
    recorder.capture(data)


@pytest.mark.vcr
def test_get_spending(recorder):
    """Test get_spending"""
    data = oecd_model.get_spending(
        countries=["united_states", "canada"],
        start_date=datetime.strptime("2020-01-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2022-01-31", "%Y-%m-%d"),
    )
    assert isinstance(data, pd.DataFrame)
    recorder.capture(data)


@pytest.mark.vcr
def test_get_trust(recorder):
    """Test get_trust"""
    data = oecd_model.get_trust(
        countries=["united_states", "canada"],
        start_date=datetime.strptime("2020-01-01", "%Y-%m-%d"),
        end_date=datetime.strptime("2022-01-31", "%Y-%m-%d"),
    )
    assert isinstance(data, pd.DataFrame)
    recorder.capture(data)
