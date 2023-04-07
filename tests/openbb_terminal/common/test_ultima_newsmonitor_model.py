# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.common.ultima_newsmonitor_model import (
    get_company_info,
    get_news,
    supported_terms,
)

MOCK_REQUEST_RESPONSE = {
    "TSLA": {
        "companyShortName": "Tesla",
        "companyFullName": "Tesla, Inc.",
        "risks": [
            "Competition Risk",
        ],
        "primary_industry": "Auto Manufacturers",
        "primary_sector": "Consumer Cyclical",
    },
    "AAPL": {
        "companyShortName": "Apple",
        "companyFullName": "Apple Inc.",
        "risks": [
            "Competition Risk",
        ],
        "primary_industry": "Consumer Electronics",
        "primary_sector": "Technology",
    },
    "FCX": {
        "companyShortName": "Freeport-McMoRan",
        "companyFullName": "Freeport-McMoRan Inc.",
        "risks": [
            "Competition Risk",
        ],
        "primary_industry": "Metals & Mining",
        "primary_sector": "Basic Materials",
    },
}


@pytest.mark.vcr
@pytest.mark.parametrize(
    "term",
    [
        (""),
        ("AAPL"),
        ("TSLA"),
        ("FCX"),
        ("asdf$#"),
    ],
)
def test_get_news(term, recorder):
    df = get_news(term=term)
    recorder.capture(df)


def test_supported_terms(mocker):
    # MOCK REQUEST
    attrs = {
        "status_code": 200,
        "json.return_value": list(MOCK_REQUEST_RESPONSE.keys()),
    }
    mock_response = mocker.Mock(**attrs)

    mocker.patch(
        target="openbb_terminal.common.ultima_newsmonitor_model.request",
        new=mocker.Mock(return_value=mock_response),
    )
    terms = supported_terms()
    assert terms == list(MOCK_REQUEST_RESPONSE.keys())


@pytest.mark.parametrize(
    "ticker, response",
    [
        ("AAPL", MOCK_REQUEST_RESPONSE["AAPL"]),
        ("TSLA", MOCK_REQUEST_RESPONSE["TSLA"]),
        ("FCX", MOCK_REQUEST_RESPONSE["FCX"]),
        ("asdf$#", {}),
    ],
)
def test_get_company_info(ticker, response, recorder, mocker):
    # MOCK SUPPORTED TERMS
    mocker.patch(
        target="openbb_terminal.common.ultima_newsmonitor_model.supported_terms",
        new=mocker.Mock(return_value=list(MOCK_REQUEST_RESPONSE.keys())),
    )

    # MOCK REQUEST
    attrs = {
        "status_code": 200,
        "json.return_value": response,
    }
    mock_response = mocker.Mock(**attrs)

    mocker.patch(
        target="openbb_terminal.common.ultima_newsmonitor_model.request",
        new=mocker.Mock(return_value=mock_response),
    )
    df = get_company_info(ticker=ticker)
    recorder.capture(df)
