"""FRED client with retry and cache-friendly failure handling."""

from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from openbb_quant_ml.service.macro_constants import (
    DEFAULT_FRED_BASE_URL,
    DEFAULT_FRED_MAX_RETRIES,
    DEFAULT_FRED_TIMEOUT_SEC,
    load_macro_config,
)


class FredClientError(RuntimeError):
    """Base FRED client error."""


class FredApiKeyMissingError(FredClientError):
    """Raised when FRED API key is missing."""


@dataclass(slots=True)
class FredClientConfig:
    """Runtime FRED client config."""

    base_url: str = DEFAULT_FRED_BASE_URL
    timeout_sec: int = DEFAULT_FRED_TIMEOUT_SEC
    max_retries: int = DEFAULT_FRED_MAX_RETRIES


def _load_config() -> FredClientConfig:
    payload = load_macro_config()
    fred_cfg = payload.get("defaults", {}).get("fred", {})
    return FredClientConfig(
        base_url=str(fred_cfg.get("base_url", DEFAULT_FRED_BASE_URL)).rstrip("/"),
        timeout_sec=int(fred_cfg.get("timeout_sec", DEFAULT_FRED_TIMEOUT_SEC)),
        max_retries=max(1, int(fred_cfg.get("max_retries", DEFAULT_FRED_MAX_RETRIES))),
    )


class FredClient:
    """Thin FRED REST wrapper."""

    def __init__(self) -> None:
        self.config = _load_config()
        self.api_key = (os.getenv("FRED_API_KEY") or "").strip()

    @property
    def has_api_key(self) -> bool:
        """Return whether API key is available."""
        return bool(self.api_key)

    def _request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise FredApiKeyMissingError("FRED_API_KEY is not configured.")

        base_params = dict(params)
        base_params["api_key"] = self.api_key
        base_params["file_type"] = "json"
        query = urlencode(base_params)
        url = f"{self.config.base_url}/{endpoint}?{query}"
        req = Request(url=url, method="GET", headers={"User-Agent": "openbb-quant-ml-macro/1.0"})

        last_error: Exception | None = None
        for attempt in range(self.config.max_retries):
            try:
                with urlopen(req, timeout=self.config.timeout_sec) as response:
                    payload = response.read().decode("utf-8")
                return json.loads(payload)
            except HTTPError as exc:
                last_error = exc
                retryable = exc.code == 429 or exc.code >= 500
                if not retryable or attempt >= self.config.max_retries - 1:
                    break
            except URLError as exc:
                last_error = exc
                if attempt >= self.config.max_retries - 1:
                    break

            sleep_sec = (2**attempt) * 0.4 + random.random() * 0.2
            time.sleep(sleep_sec)

        if isinstance(last_error, HTTPError):
            raise FredClientError(f"FRED request failed with HTTP {last_error.code}.") from last_error
        if last_error is not None:
            raise FredClientError(f"FRED request failed: {last_error}") from last_error
        raise FredClientError("FRED request failed for unknown reason.")

    def get_series_metadata(self, series_id: str) -> dict[str, Any]:
        """Fetch metadata for one series id."""
        payload = self._request("series", {"series_id": series_id})
        entries = payload.get("seriess") or []
        if not entries:
            raise FredClientError(f"FRED series not found: {series_id}")
        item = dict(entries[0])
        return {
            "series_id": str(item.get("id", series_id)),
            "title": item.get("title"),
            "frequency": item.get("frequency_short") or item.get("frequency"),
            "units": item.get("units"),
            "notes": item.get("notes"),
        }

    def search_series(self, query: str, limit: int = 25) -> list[dict[str, Any]]:
        """Search FRED series by keyword."""
        payload = self._request(
            "series/search",
            {"search_text": query, "limit": max(1, min(int(limit), 100)), "order_by": "search_rank"},
        )
        rows = payload.get("seriess") or []
        return [
            {
                "series_id": str(item.get("id", "")),
                "title": item.get("title"),
                "frequency": item.get("frequency_short") or item.get("frequency"),
                "units": item.get("units"),
                "notes": item.get("notes"),
            }
            for item in rows
            if item.get("id")
        ]

    def get_series_observations(
        self,
        series_id: str,
        start: date | None = None,
        end: date | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch time-series observations."""
        params: dict[str, Any] = {"series_id": series_id}
        if start:
            params["observation_start"] = start.isoformat()
        if end:
            params["observation_end"] = end.isoformat()
        payload = self._request("series/observations", params)
        rows = payload.get("observations") or []
        out: list[dict[str, Any]] = []
        fetched_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        for row in rows:
            raw_value = row.get("value")
            value: float | None
            if raw_value in {None, ".", ""}:
                value = None
            else:
                try:
                    value = float(raw_value)
                except (TypeError, ValueError):
                    value = None
            out.append(
                {
                    "date": row.get("date"),
                    "value": value,
                    "realtime_start": row.get("realtime_start"),
                    "realtime_end": row.get("realtime_end"),
                    "fetched_at": fetched_at,
                }
            )
        return out
