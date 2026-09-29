"""Build the packaged map of FRED releases and their tables."""

import asyncio
import json
from pathlib import Path
from typing import Any

ASSET = Path(__file__).resolve().parent.parent / "assets" / "release_map.json"
DEPTH = 2
CONCURRENCY = 4
TIMEOUT = 60
TRIES = 6


async def _get(url: str) -> dict | None:
    """Read one endpoint, or nothing at all when it cannot be read."""
    from openbb_fred.utils.rate_limiter import fred_get

    for attempt in range(TRIES):
        try:
            return await fred_get(url, timeout=TIMEOUT) or {}
        except Exception as error:  # noqa: BLE001
            if attempt == TRIES - 1:
                print(f"  ! unreadable {url.split('&api_key', maxsplit=1)[0]}")
                print(f"    {type(error).__name__}: {error}")

                return None

            await asyncio.sleep(2**attempt)

    return None


async def _elements(
    api_key: str, release_id: str, element_id: str | None
) -> list[dict]:
    """Read the sections and tables directly under one node."""
    from openbb_fred.utils.api import build_url

    url = build_url(
        "release/tables", api_key, release_id=release_id, element_id=element_id
    )
    payload = await _get(url) or {}

    return [
        {
            "element_id": str(v["element_id"]),
            "name": v.get("name") or "",
            "type": v.get("type"),
        }
        for v in (payload.get("elements") or {}).values()
        if v and v.get("type") in ("section", "table") and v.get("element_id")
    ]


async def _tree(api_key: str, release_id: str) -> list[dict]:
    """Walk one release to the depth the picker offers."""
    found: list[dict] = []

    async def walk(element_id: str | None, depth: int) -> None:
        if depth > DEPTH:
            return

        for node in await _elements(api_key, release_id, element_id):
            found.append(
                {
                    "element_id": node["element_id"],
                    "name": node["name"],
                    "type": node["type"],
                    "depth": depth,
                }
            )

            if node["type"] == "section":
                await walk(node["element_id"], depth + 1)

    await walk(None, 0)

    return found


async def build(credentials: dict) -> dict[str, Any]:
    """Resolve every publishing release and the tables under it.

    Parameters
    ----------
    credentials : dict
        The provider credentials.

    Returns
    -------
    dict
        The releases, each carrying its name and its element tree.
    """
    from openbb_fred.utils.api import build_url
    from openbb_fred.utils.release_tables import current, release_series

    api_key = credentials.get("fred_api_key") or ""
    payload = await _get(build_url("releases", api_key, limit=1000)) or {}
    releases = {
        str(r["id"]): r.get("name") or str(r["id"])
        for r in payload.get("releases") or []
    }
    print(f"releases: {len(releases)}")

    gate = asyncio.Semaphore(CONCURRENCY)
    resolved: dict[str, Any] = {}
    retired: list[str] = []
    done = 0

    async def one(release_id: str, name: str) -> None:
        nonlocal done

        async with gate:
            series = await release_series(release_id, credentials)
            live = {s["series_id"] for s in series if current(s)}

            if not live:
                done += 1
                retired.append(release_id)
                print(
                    f"  retired {release_id:>4} {name[:56]:56}"
                    f" {len(series):>5} series, none current"
                )
                return

            elements = await _tree(api_key, release_id)

        tables = sum(1 for e in elements if e["type"] == "table")
        done += 1
        resolved[release_id] = {"name": name, "elements": elements}

        if done % 25 == 0:
            print(f"  [{done}/{len(releases)}] resolved")

        if not tables and not elements:
            return

        if not tables:
            print(f"  ! {release_id:>4} {name[:56]:56} sections but no table")

    await asyncio.gather(*(one(r, n) for r, n in releases.items()))

    print(f"\nretired releases dropped: {len(retired)} {sorted(retired, key=int)}")
    print(f"releases kept: {len(resolved)}")

    return {r: resolved[r] for r in sorted(resolved, key=lambda x: int(x))}


def main() -> None:
    """Write the map to the packaged asset."""
    from openbb_core.app.service.user_service import UserService

    credentials = UserService().default_user_settings.credentials.model_dump(
        mode="json"
    )

    if not credentials.get("fred_api_key"):
        raise SystemExit("A FRED API key is required to build the release map.")

    resolved = asyncio.run(build(credentials))
    ASSET.write_text(json.dumps(resolved, indent=1) + "\n", encoding="utf-8")
    tables = sum(len(v["elements"]) for v in resolved.values())
    print(f"\nwrote {ASSET} - {len(resolved)} releases, {tables} elements")


if __name__ == "__main__":
    main()
