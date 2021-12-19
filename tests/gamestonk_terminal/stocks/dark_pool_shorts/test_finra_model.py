# IMPORTATION STANDARD
import gzip
import json

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.dark_pool_shorts import finra_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
def test_getFINRAweeks(recorder):
    result_df = finra_model.getFINRAweeks(
        tier="T1",
        is_ats=True,
    )

    recorder.capture(result_df)


@pytest.mark.vcr
def test_getFINRAdata_offset(recorder):
    response = finra_model.getFINRAdata_offset(
        weekStartDate="2021-11-01",
        tier="T1",
        ticker="TSLA",
        is_ats=False,
        offset=0,
    )

    recorder.capture(response.text)


@pytest.mark.vcr
def test_getTickerFINRAdata(recorder):
    result_list = finra_model.getTickerFINRAdata(
        ticker="RIVN",
    )

    recorder.capture_list(result_list)


def filter_test_getATSdata(response):
    content = gzip.decompress(response["body"]["string"]).decode()
    content_json = json.loads(content)
    if len(content_json) > 10:
        new_content = json.dumps(content_json[:10])
        response["body"]["string"] = gzip.compress(new_content.encode())
    return response


@pytest.mark.skip(reason="Weird behaviour on 3.9 MAC OS.")
@pytest.mark.vcr(before_record_response=filter_test_getATSdata)
def test_getATSdata(recorder):
    result_list = finra_model.getATSdata(
        num_tickers_to_filter=2,
        tier_ats="T1",
    )

    recorder.capture_list(result_list)
