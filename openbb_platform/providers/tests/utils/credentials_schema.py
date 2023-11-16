"""Provider credentials schema used for unit test."""

from typing import Dict, Tuple

test_credentials: Dict[str, Tuple[str, str]] = {
    "benzinga": ("token", "MOCK_TOKEN"),
    "alpha_vantage": ("apikey", "MOCK_API_KEY"),
    "fmp": ("apikey", "MOCK_API_KEY"),
    "polygon": ("apiKey", "MOCK_API_KEY"),
    "nasdaq": ("x-api-token", "MOCK_API_KEY"),
    "fred": ("api_key", "MOCK_API_KEY"),
    "intrinio": ("api_key", "MOCK_API_KEY"),
    "tiingo": ("token", "MOCK_TOKEN"),
}
