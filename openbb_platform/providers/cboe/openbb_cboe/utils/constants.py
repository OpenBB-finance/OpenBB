"""Cboe Provider Constants."""

from openbb_core.app.service.system_service import SystemService

API_PREFIX = (
    SystemService()
    .system_settings.python_settings.model_dump()
    .get("api_settings", {})
    .get("prefix", "")
    or "/api/v1"
)

EQUITY_CHOICES_ENDPOINT = f"{API_PREFIX}/cboe/equity/symbol_choices"
INDEX_CHOICES_ENDPOINT = f"{API_PREFIX}/cboe/index/symbol_choices"
CONSTITUENT_CHOICES_ENDPOINT = f"{API_PREFIX}/cboe/index/constituent_choices"
DOCUMENT_CHOICES_ENDPOINT = f"{API_PREFIX}/cboe/index/document_choices"
TICKERS_ENDPOINT = f"{API_PREFIX}/cboe/options/get_tickers"
