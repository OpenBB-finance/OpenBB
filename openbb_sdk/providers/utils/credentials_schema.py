"""Provider credentials schema used for unit test."""

from typing import Dict

test_credentials: Dict[str, Dict[str, str]] = {
    "benzinga": {
        "token": "MOCK_TOKEN",
    },
    "alpha_vantage": {
        "api_key": "MOCK_API_KEY",
    },
    "fmp": {
        "apikey": "MOCK_API_KEY",
    },
    "polygon": {
        "apiKey": "MOCK_API_KEY",
    },
    "quandl": {
        "api_key": "MOCK_API_KEY",
    },
    "fred": {
        "api_key": "MOCK_API_KEY",
    },
    "intrinio": {
        "api_key": "MOCK_API_KEY",
    },
}
