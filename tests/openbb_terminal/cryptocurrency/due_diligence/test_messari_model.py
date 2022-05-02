# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.due_diligence import messari_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("x-messari-api-key", "mock_x-messari-api-key"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin,interval,start,end",
    [
        ("btc", "1d", "2022-01-10", "2022-03-08"),
    ],
)
def test_get_marketcap_dominance(coin, interval, start, end, recorder):
    df = messari_model.get_marketcap_dominance(
        coin=coin, interval=interval, start=start, end=end
    )
    recorder.capture(df)


@pytest.mark.vcr
def test_get_available_timeseries(recorder):
    df = messari_model.get_available_timeseries()
    recorder.capture(df)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin",
    [
        ("aave"),
    ],
)
def test_get_coin_tokenomics(coin, recorder):
    df = messari_model.get_coin_tokenomics(symbol=coin)
    recorder.capture(df)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin",
    [
        ("eth"),
    ],
)
def test_get_fundraising(coin, recorder):
    (
        summary,
        df_sales_rounds,
        df_treasury_accs,
        df_details,
    ) = messari_model.get_fundraising(symbol=coin)
    recorder.capture_list([summary, df_sales_rounds, df_treasury_accs, df_details])


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin",
    [
        ("eth"),
    ],
)
def test_get_governance(coin, recorder):
    summary, df = messari_model.get_governance(symbol=coin)
    recorder.capture_list([summary, df])


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin",
    [
        ("eth"),
    ],
)
def test_get_investors(coin, recorder):
    df_individuals, df_organizations = messari_model.get_investors(symbol=coin)
    recorder.capture_list([df_individuals, df_organizations])


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin",
    [
        ("eth"),
    ],
)
def test_get_team(coin, recorder):
    df_individuals, df_organizations = messari_model.get_team(symbol=coin)
    recorder.capture_list([df_individuals, df_organizations])


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin",
    [
        ("eth"),
    ],
)
def test_get_links(coin, recorder):
    df = messari_model.get_links(symbol=coin)
    recorder.capture(df)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin,interval,start,end,timeseries_id",
    [
        ("btc", "1d", "2022-01-10", "2022-03-08", "sply.circ"),
    ],
)
def test_get_messari_timeseries(coin, interval, start, end, timeseries_id, recorder):
    df, _, _ = messari_model.get_messari_timeseries(
        coin=coin, interval=interval, start=start, end=end, timeseries_id=timeseries_id
    )
    recorder.capture(df)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin",
    [
        ("eth"),
    ],
)
def test_get_project_product_info(coin, recorder):
    df_info, df_repos, df_audits, df_vulns = messari_model.get_project_product_info(
        symbol=coin
    )
    recorder.capture_list([df_info, df_repos, df_audits, df_vulns])


@pytest.mark.vcr
@pytest.mark.parametrize(
    "coin",
    [
        ("eth"),
    ],
)
def test_get_roadmap(coin, recorder):
    df = messari_model.get_roadmap(symbol=coin)
    recorder.capture(df)
