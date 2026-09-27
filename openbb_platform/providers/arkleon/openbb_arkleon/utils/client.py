"""Authenticated, point-in-time requests to the Arkleon facts endpoint."""

import os

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.helpers import make_request

BASE_URL = "https://arkleon.com/v1"


def resolve_api_key(credentials: dict | None) -> str:
    """Use the explicit credential first, then the environment."""
    api_key = (credentials or {}).get("arkleon_api_key") or os.environ.get(
        "ARKLEON_API_KEY"
    )
    if api_key:
        return api_key
    raise OpenBBError(
        "Missing Arkleon API key: set ARKLEON_API_KEY or "
        "obb.user.credentials.arkleon_api_key."
    )


def fetch_facts(
    api_key: str,
    cik: int,
    as_of: str,
    tag: str,
    duration_quarters: int,
    unit: str,
) -> list[dict]:
    """Read every page with the same filing-date cutoff and filters."""
    params = {
        "as_of": as_of,
        "cik": cik,
        "tag": tag,
        "duration_quarters": duration_quarters,
        "unit": unit,
        "limit": 1000,
    }
    facts = []
    while True:
        response = make_request(
            f"{BASE_URL}/facts",
            method="GET",
            timeout=30,
            headers={"Authorization": f"Bearer {api_key}"},
            params=dict(params),
        )
        if response.status_code != 200:
            try:
                body = response.json()
            except ValueError:
                body = {}
            error = (body.get("error") if isinstance(body, dict) else None) or "unknown"
            raise OpenBBError(
                f"Arkleon /v1/facts returned {response.status_code}: {error}"
            )
        body = response.json()
        facts.extend(body["data"])
        cursor = body["next_cursor"]
        if cursor is None:
            return facts
        params["cursor"] = cursor
