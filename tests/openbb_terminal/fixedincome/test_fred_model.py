import pytest
from pandas import DataFrame

from openbb_terminal.fixedincome import fred_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize("inflation", [True, False])
def test_yield_curve(recorder, inflation):
    data = fred_model.get_yield_curve(date="2023-02-08", inflation_adjusted=inflation)

    assert isinstance(data, DataFrame)
    recorder.capture(data)


@pytest.mark.record_http
@pytest.mark.parametrize(
    "series_id, kwargs",
    [
        ("DGS10", {"start_date": "2020-01-01", "end_date": "2020-02-01"}),
    ],
)
def test_get_series_data(series_id, kwargs):
    fred_model.get_series_data(series_id, **kwargs)


@pytest.mark.record_http
@pytest.mark.parametrize(
    "parameter, start_date, end_date",
    [
        ("overnight", "2020-01-01", "2020-02-01"),
    ],
)
def test_get_sofr(parameter, start_date, end_date):
    df = fred_model.get_sofr(parameter, start_date, end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "parameter, start_date, end_date",
    [
        ("rate", "2020-01-01", "2020-02-01"),
    ],
)
def test_get_sonia(parameter, start_date, end_date):
    df = fred_model.get_sonia(parameter, start_date, end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "parameter, start_date, end_date",
    [
        ("overnight", "2020-01-01", "2020-02-01"),
    ],
)
def test_get_ameribor(parameter, start_date, end_date):
    df = fred_model.get_ameribor(parameter, start_date, end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "parameter, kwargs",
    [("monthly", dict())],
)
def test_get_fed(parameter, kwargs):
    df = fred_model.get_fed(parameter, **kwargs)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize("start_date, end_date", [("2023-01-01", "2023-03-30")])
def test_get_iorb(start_date, end_date):
    df = fred_model.get_iorb(start_date=start_date, end_date=end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
def test_get_projection():
    df = fred_model.get_projection()

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "parameter, start_date, end_date",
    [
        ("daily_excl_weekend", "2020-01-01", "2020-02-01"),
    ],
)
def test_get_dwpcr(parameter, start_date, end_date):
    df = fred_model.get_dwpcr(parameter, start_date, end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
def test_get_ecb():
    df = fred_model.get_ecb()

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "parameter, maturity, start_date, end_date",
    [
        ("tbill", "4_week", "2020-01-01", "2023-02-01"),
    ],
)
def test_get_usrates(parameter, maturity, start_date, end_date):
    df = fred_model.get_usrates(parameter, maturity, start_date, end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.parametrize(
    "data_type, category, area, grade, start_date, end_date",
    [
        ("yield", "all", "us", "non_sovereign", "2020-01-01", "2023-02-01"),
    ],
)
def test_get_icebofa(data_type, category, area, grade, start_date, end_date):
    df = fred_model.get_icebofa(data_type, category, area, grade, start_date, end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "data_type, kwargs",
    [
        ("baa", {"start_date": "2020-01-01", "end_date": "2023-02-01"}),
    ],
)
def test_get_moody(data_type, kwargs):
    df = fred_model.get_moody(data_type, **kwargs)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "maturity, category, grade, start_date, end_date",
    [
        ("30d", "financial", "aa", "2020-01-01", "2023-02-01"),
    ],
)
def test_get_cp(maturity, category, grade, start_date, end_date):
    df = fred_model.get_cp(maturity, category, grade, start_date, end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "maturity, category, start_date, end_date",
    [
        (["10y"], ["spot_rate"], "2020-01-01", "2023-02-01"),
    ],
)
def test_get_spot(maturity, category, start_date, end_date):
    df = fred_model.get_spot(maturity, category, start_date, end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize("date, par", [("2023-03-30", False)])
def test_get_hqm(date, par):
    df = fred_model.get_hqm(date=date, par=par)

    assert isinstance(df[0], DataFrame)
    assert not df[0].empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "parameter, start_date, end_date",
    [
        ("3_month", "2020-01-01", "2021-02-01"),
    ],
)
def test_get_tbffr(parameter, start_date, end_date):
    df = fred_model.get_tbffr(parameter, start_date, end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "category, area, grade, options, start_date, end_date",
    [
        ("all", "us", "non_sovereign", False, "2020-01-01", "2021-02-01"),
    ],
)
def test_get_icespread(category, area, grade, options, start_date, end_date):
    df = fred_model.get_icespread(category, area, grade, options, start_date, end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "parameter, start_date, end_date",
    [
        ("10_year", "2020-01-01", "2021-02-01"),
    ],
)
def test_get_ffrmc(parameter, start_date, end_date):
    df = fred_model.get_ffrmc(parameter, start_date, end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "parameter, start_date, end_date",
    [
        ("3_month", "2020-01-01", "2021-02-01"),
    ],
)
def test_get_tmc(parameter, start_date, end_date):
    df = fred_model.get_tmc(parameter, start_date, end_date)

    assert isinstance(df, DataFrame)
    assert not df.empty
