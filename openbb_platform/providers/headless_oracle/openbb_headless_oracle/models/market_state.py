from __future__ import annotations

from datetime import datetime
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.market_state import (
    MarketStateData,
    MarketStateQueryParams,
)
from openbb_core.provider.utils.exchange_utils import Exchange
from pydantic import Field


class HeadlessOracleMarketStateQueryParams(MarketStateQueryParams):
    exchange: Exchange = Field(description="Exchange MIC, acronym, or name to check market state for.")


class HeadlessOracleMarketStateFetcher(
    Fetcher[
        HeadlessOracleMarketStateQueryParams,
        MarketStateData,
    ]
):
    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> HeadlessOracleMarketStateQueryParams:
        return HeadlessOracleMarketStateQueryParams(**params)

    @staticmethod
    def extract_data(
        query: HeadlessOracleMarketStateQueryParams,
        credentials: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import make_request

        url = f"https://headlessoracle.com/v5/demo?mic={query.exchange.mic}"

        try:
            response = make_request(url, timeout=30)
            if response.status_code != 200:
                raise OpenBBError(f"Headless Oracle request failed with status {response.status_code}: {response.text}")

            return response.json()
        except OpenBBError:
            raise
        except Exception as error:
            raise OpenBBError(error) from error

    @staticmethod
    def transform_data(
        query: HeadlessOracleMarketStateQueryParams,
        data: dict[str, Any],
        **kwargs: Any,
    ) -> MarketStateData:
        payload = data.get("receipt")
        if not isinstance(payload, dict):
            raise OpenBBError("Headless Oracle response did not include a valid receipt payload.")

        missing_fields = [field for field in ("mic", "status", "issued_at", "expires_at") if not payload.get(field)]
        if missing_fields:
            raise OpenBBError(
                f"Headless Oracle receipt payload is missing required field(s): {', '.join(missing_fields)}"
            )

        status = str(payload.get("status") or "UNKNOWN").upper()
        issued_at = HeadlessOracleMarketStateFetcher._parse_datetime(payload.get("issued_at"))
        expires_at = HeadlessOracleMarketStateFetcher._parse_datetime(payload.get("expires_at"))
        ttl_seconds = (
            int((expires_at - issued_at).total_seconds()) if issued_at is not None and expires_at is not None else None
        )

        return MarketStateData(
            exchange=query.exchange.acronym,
            mic=str(payload.get("mic") or query.exchange.mic),
            status=status,
            is_open=status == "OPEN",
            issued_at=issued_at,
            expires_at=expires_at,
            ttl_seconds=ttl_seconds,
            issuer=payload.get("issuer"),
            source=payload.get("source"),
            halt_detection=payload.get("halt_detection"),
            receipt_mode=payload.get("receipt_mode"),
            schema_version=payload.get("schema_version"),
            public_key_id=payload.get("public_key_id") or payload.get("key_id"),
            signature=payload.get("signature"),
        )

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
