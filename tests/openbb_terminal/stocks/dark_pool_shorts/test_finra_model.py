# IMPORTATION STANDARD
import gzip
import json

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.dark_pool_shorts import finra_model


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
        start_date="2021-11-01",
        symbol="TSLA",
        tier="T1",
        is_ats=False,
        offset=0,
    )

    recorder.capture(response.text)


@pytest.mark.vcr
def test_getTickerFINRAdata(recorder):
    result_list = finra_model.getTickerFINRAdata(
        symbol="RIVN",
    )

    recorder.capture_list(result_list)


def filter_json_data(response):
    """To reduce cassette size."""

    headers = response["headers"]
    if "FILTERED" in headers:
        return response

    if "gzip" in headers.get("Content-Encoding", {}) or "gzip" in headers.get(
        "content-encoding", {}
    ):
        limit = 10
        content_gz = response["body"]["string"]
        content_json = gzip.decompress(content_gz).decode()
        content = json.loads(content_json)

        if isinstance(content, list):
            new_content = content[:limit]
        elif isinstance(content, dict):
            new_content = {k: content[k] for k in list(content)[:limit]}
        else:
            raise AttributeError(f"Content type not supported : {content}")

        new_content_json = json.dumps(new_content)
        new_content_gz = gzip.compress(new_content_json.encode())
        response["body"]["string"] = new_content_gz
        response["headers"]["FILTERED"] = ["TRUE"]

    return response


@pytest.mark.vcr(before_record_response=filter_json_data)
def test_getATSdata(recorder):
    df_ats, d_ats_reg = finra_model.getATSdata(
        limit=2,
        tier_ats="T1",
    )

    d_ats_reg = {k: round(v, 9) for k, v in d_ats_reg.items()}

    recorder.capture_list([df_ats, d_ats_reg])
