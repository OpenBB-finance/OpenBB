import asyncio
import json
from datetime import date
from pathlib import Path

import pytest
import urllib3
import vcr
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_cftc.utils import search

pytestmark = pytest.mark.cassette

CLP_UPI = "NA/Swap OIS CLP"

BUSY_DAY = date(2026, 7, 15)
MIN_NOTIONAL = 100_000_000_000

QUIET_DAY = date(2026, 7, 12)

DEFAULT_MATCHERS = ["method", "scheme", "host", "port", "path", "query"]
BODY_MATCHERS = [*DEFAULT_MATCHERS, "body"]

_RECORD_DIR = Path(__file__).parent / "record" / "http" / "test_search_http"
_SUFFIX = f"_urllib3_v{urllib3.__version__.split('.')[0]}.yaml"


def canonical_json_body(request):
    if isinstance(request.body, dict):
        request.body = json.dumps(request.body)

    return request


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "before_record_request": canonical_json_body,
        "match_on": BODY_MATCHERS,
    }


def _clp_payload(min_notional: float = 0.0) -> dict:
    return search.build_search_payload(
        "rates",
        currency="CLP",
        upi_short_name=CLP_UPI,
        min_notional=min_notional,
    )


def _windowed(payload: dict, start: date, end: date) -> dict:
    payload = dict(payload)
    payload["disseminationDateTimeLow"] = search.format_search_datetime(start)
    payload["disseminationDateTimeHigh"] = search.format_search_datetime(
        end, end_of_day=True
    )

    return payload


def _busy_payload() -> dict:
    return _windowed(_clp_payload(MIN_NOTIONAL), BUSY_DAY, BUSY_DAY)


def _quiet_payload() -> dict:
    return _windowed(_clp_payload(), QUIET_DAY, QUIET_DAY)


def _malformed_payload() -> dict:
    payload = _clp_payload()
    payload["disseminationDateTimeLow"] = "07/13/2026"
    payload["disseminationDateTimeHigh"] = "07/15/2026"

    return payload


@pytest.mark.record_http
def test_post_search_returns_a_narrow_windows_trade_list():
    rows = asyncio.run(search.post_search(_busy_payload()))

    assert rows

    for row in rows:
        assert row["uniqueProductIdentifierShortName"] == "NA%2FSwap%20OIS%20CLP"
        assert row["notionalCurrencyLeg1"] == "CLP"
        assert row["disseminationTimestamp"].startswith(BUSY_DAY.isoformat())
        assert float(row["fixedRateLeg1"]) > 0
        assert row["notionalAmountLeg1"].endswith("+")
        assert float(row["notionalAmountLeg1"].rstrip("+").replace(",", "")) >= (
            MIN_NOTIONAL
        )

    mapped = search.map_search_record(rows[0])

    assert mapped["UPI FISN"] == "NA/Swap OIS CLP"
    assert mapped["UPI Underlier Name"].startswith("CLP-")
    assert mapped["Notional currency-Leg 1"] == "CLP"
    assert mapped["Action type"] == "NEWT"
    assert mapped["Dissemination Identifier"]


@pytest.mark.record_http
def test_post_search_raises_on_an_error_returned_with_http_200():
    with pytest.raises(OpenBBError, match="Dissemination Date Time format"):
        asyncio.run(search.post_search(_malformed_payload()))


@pytest.mark.record_http
def test_post_search_returns_no_rows_for_a_quiet_window():
    assert asyncio.run(search.post_search(_quiet_payload())) == []


@pytest.mark.record_http
def test_two_searches_share_one_cassette():
    with pytest.raises(OpenBBError, match="Dissemination Date Time format"):
        asyncio.run(search.post_search(_malformed_payload()))

    assert asyncio.run(search.post_search(_quiet_payload())) == []


def test_body_matching_keeps_the_two_searches_apart():
    cassette = _RECORD_DIR / f"test_two_searches_share_one_cassette{_SUFFIX}"

    with vcr.use_cassette(
        str(cassette),
        record_mode="none",
        before_record_request=canonical_json_body,
        match_on=BODY_MATCHERS,
    ):
        assert asyncio.run(search.post_search(_quiet_payload())) == []

        with pytest.raises(OpenBBError, match="Dissemination Date Time format"):
            asyncio.run(search.post_search(_malformed_payload()))

    with vcr.use_cassette(
        str(cassette),
        record_mode="none",
        before_record_request=canonical_json_body,
        match_on=DEFAULT_MATCHERS,
    ):
        with pytest.raises(OpenBBError, match="Dissemination Date Time format"):
            asyncio.run(search.post_search(_quiet_payload()))
