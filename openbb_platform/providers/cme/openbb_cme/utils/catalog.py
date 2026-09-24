"""CME Group product catalog and contract specification helpers."""

import asyncio
import copy
import json
import os
import re
import tempfile
import time
import warnings
from contextlib import suppress
from html import unescape
from pathlib import Path
from typing import Any, Literal

from openbb_core.app.utils import get_user_cache_directory

from openbb_cme.utils import helpers
from openbb_cme.utils.client import CMEHttpClient, CMERequestError

ProductType = Literal["Futures", "Options"]


def _float_env(name: str, default: float) -> float:
    """Read a non-negative float environment setting."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return max(float(raw), 0.0)
    except (TypeError, ValueError):
        return default


_CACHE_TTL_SECONDS = _float_env("OPENBB_CME_CATALOG_TTL", 6 * 60 * 60)
_STALE_CACHE_TTL_SECONDS = _float_env("OPENBB_CME_CATALOG_STALE_TTL", 7 * 24 * 60 * 60)
_PRODUCT_CACHE: dict[ProductType, tuple[float, list[dict[str, Any]]]] = {}
_REFRESH_TASKS: dict[tuple[int, ProductType], asyncio.Task[list[dict[str, Any]]]] = {}


def _copy_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a defensive copy of catalog metadata."""
    return copy.deepcopy(products)


def _catalog_cache_path(product_type: ProductType) -> Path | None:
    """Return the persistent catalog cache path, if settings are available."""
    try:
        cache_root = Path(get_user_cache_directory()).expanduser()
    except (OSError, TypeError, ValueError, KeyError):
        return None
    return cache_root / "cme" / f"product_catalog_{product_type.lower()}.json"


def _valid_products(value: Any, product_type: ProductType) -> bool:
    """Validate the minimum identity fields required from a cached catalog."""
    return (
        bool(value)
        and isinstance(value, list)
        and all(
            isinstance(row, dict)
            and isinstance(row.get("product_id"), int)
            and bool(row.get("symbol"))
            and isinstance(row.get("name"), str)
            and row.get("product_type") == product_type
            and isinstance(row.get("asset_class"), str)
            and isinstance(row.get("exchange"), str)
            and isinstance(row.get("codes"), dict)
            for row in value
        )
    )


def _read_disk_cache(
    product_type: ProductType,
) -> tuple[float, list[dict[str, Any]]] | None:
    """Read and validate a persistent product catalog cache."""
    path = _catalog_cache_path(product_type)
    if path is None or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        fetched_at = float(payload["fetched_at"])
        products = payload["products"]
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None
    if not _valid_products(products, product_type):
        return None
    return fetched_at, products


def _write_disk_cache(
    product_type: ProductType,
    fetched_at: float,
    products: list[dict[str, Any]],
) -> None:
    """Atomically persist a validated product catalog."""
    path = _catalog_cache_path(product_type)
    if path is None:
        return
    temporary: str | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as cache_file:
            temporary = cache_file.name
            json.dump(
                {
                    "schema_version": 1,
                    "fetched_at": fetched_at,
                    "products": products,
                },
                cache_file,
                separators=(",", ":"),
            )
            cache_file.flush()
            os.fsync(cache_file.fileno())
        Path(temporary).replace(path)
    except (OSError, TypeError, ValueError):
        if temporary:
            with suppress(OSError):
                Path(temporary).unlink(missing_ok=True)


def _parse_integer(value: Any) -> int | None:
    """Parse a CME count field containing comma separators."""
    if value in (None, "", "-"):
        return None
    try:
        return int(str(value).replace(",", ""))
    except ValueError:
        return None


def _plain_text(value: Any) -> str | None:
    """Convert an HTML contract-specification value to readable plain text."""
    if value in (None, "", "-"):
        return None
    if isinstance(value, dict | list):
        return None
    text = re.sub(r"<br\s*/?>", "\n", str(value), flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text).replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip() or None


def _normalize_product(row: dict[str, Any]) -> dict[str, Any]:
    """Normalize one product-slate row."""
    codes = {
        "product": row.get("prodCode"),
        "clearing": row.get("clearing"),
        "globex": row.get("globex"),
        "clearport": row.get("cpc"),
        "floor": row.get("floor"),
    }
    codes = {key: value for key, value in codes.items() if value not in (None, "-")}
    symbol = (
        codes.get("globex")
        or codes.get("clearing")
        or codes.get("product")
        or str(row.get("id", ""))
    )
    return {
        "product_id": int(row["id"]),
        "guid": row.get("guid"),
        "symbol": symbol,
        "name": row.get("name"),
        "product_type": row.get("cleared"),
        "asset_class": row.get("group"),
        "subgroup": row.get("subGroup"),
        "category": None if row.get("cat") == "-" else row.get("cat"),
        "subcategory": None if row.get("subCat") == "-" else row.get("subCat"),
        "exchange": row.get("exch"),
        "venues": str(row.get("venues", "")).split(),
        "globex_traded": bool(row.get("globexTraded")),
        "floor_traded": bool(row.get("floorTraded")),
        "volume": _parse_integer(row.get("vol")),
        "open_interest": _parse_integer(row.get("oi")),
        "codes": codes,
        "specification_url": (
            f"{helpers.BASE_URL}{row['url']}" if row.get("url") else None
        ),
    }


async def _fetch_product_catalog(
    product_type: ProductType,
    client: CMEHttpClient,
) -> list[dict[str, Any]]:
    """Fetch, validate, and normalize every product-slate page."""
    base_url = (
        f"{helpers.BASE_URL}/services/product-slate"
        "?sortAsc=true&sortField=name&pageNumber={page}"
        f"&cleared={product_type}"
    )
    first_url = base_url.format(page=1)
    first = await helpers._get_json(first_url, client)
    if not isinstance(first, dict) or not isinstance(first.get("products"), list):
        raise CMERequestError(
            f"CME returned an invalid {product_type.lower()} product catalog.",
            url=first_url,
        )

    props = first.get("props", {})
    try:
        page_total = int(props.get("pageTotal", 1))
    except (TypeError, ValueError) as exc:
        raise CMERequestError(
            f"CME returned invalid {product_type.lower()} catalog pagination.",
            url=first_url,
        ) from exc
    if not 1 <= page_total <= 100:
        raise CMERequestError(
            f"CME returned unsafe {product_type.lower()} catalog pagination.",
            url=first_url,
        )

    remaining = await asyncio.gather(
        *[
            helpers._get_json(base_url.format(page=page), client)
            for page in range(2, page_total + 1)
        ]
    )
    pages = [first, *remaining]
    if any(
        not isinstance(page, dict) or not isinstance(page.get("products"), list)
        for page in pages
    ):
        raise CMERequestError(
            f"CME returned an incomplete {product_type.lower()} product catalog.",
            url=first_url,
        )

    try:
        products = [
            _normalize_product(row)
            for page in pages
            if isinstance(page, dict)
            for row in page.get("products", [])
            if isinstance(row, dict) and row.get("id") is not None
        ]
    except (KeyError, TypeError, ValueError) as exc:
        raise CMERequestError(
            f"CME returned malformed {product_type.lower()} product metadata.",
            url=first_url,
        ) from exc
    if not _valid_products(products, product_type):
        raise CMERequestError(
            f"CME returned no valid {product_type.lower()} products.",
            url=first_url,
        )
    expected_total = props.get("total")
    if expected_total is not None:
        try:
            complete = len(products) == int(expected_total)
        except (TypeError, ValueError):
            complete = False
        if not complete:
            raise CMERequestError(
                (
                    f"CME returned an incomplete {product_type.lower()} catalog "
                    f"({len(products)} of {expected_total} products)."
                ),
                url=first_url,
            )
    product_ids = [row["product_id"] for row in products]
    if len(product_ids) != len(set(product_ids)):
        raise CMERequestError(
            f"CME returned duplicate {product_type.lower()} catalog pages.",
            url=first_url,
        )
    return products


async def _refresh_product_catalog(
    product_type: ProductType,
    client: CMEHttpClient | None,
) -> list[dict[str, Any]]:
    """Refresh a catalog and update both memory and persistent caches."""
    if client is None:
        async with CMEHttpClient() as owned_client:
            products = await _fetch_product_catalog(product_type, owned_client)
    else:
        products = await _fetch_product_catalog(product_type, client)

    fetched_at = time.time()
    _PRODUCT_CACHE[product_type] = (fetched_at, products)
    _write_disk_cache(product_type, fetched_at, products)
    return products


async def fetch_product_catalog(
    product_type: ProductType,
    *,
    use_cache: bool = True,
    client: CMEHttpClient | None = None,
) -> list[dict[str, Any]]:
    """Return a complete CME catalog with fresh and stale-cache safeguards."""
    now = time.time()
    stale: tuple[float, list[dict[str, Any]]] | None = None
    if use_cache:
        memory = _PRODUCT_CACHE.get(product_type)
        if memory and max(now - memory[0], 0.0) <= _CACHE_TTL_SECONDS:
            return _copy_products(memory[1])
        disk = _read_disk_cache(product_type)
        candidates = [entry for entry in (memory, disk) if entry is not None]
        if candidates:
            newest = max(candidates, key=lambda entry: entry[0])
            age = max(now - newest[0], 0.0)
            if age <= _CACHE_TTL_SECONDS:
                _PRODUCT_CACHE[product_type] = newest
                return _copy_products(newest[1])
            if age <= _STALE_CACHE_TTL_SECONDS:
                stale = newest

    if not use_cache:
        return _copy_products(await _refresh_product_catalog(product_type, client))

    loop = asyncio.get_running_loop()
    key = (id(loop), product_type)
    task = _REFRESH_TASKS.get(key)
    if task is None or task.done():
        task = loop.create_task(_refresh_product_catalog(product_type, client))
        _REFRESH_TASKS[key] = task
    try:
        products = await asyncio.shield(task)
        return _copy_products(products)
    except Exception:
        if stale is None:
            raise
        warnings.warn(
            (
                f"CME {product_type.lower()} catalog refresh failed; "
                "using the most recent cached catalog."
            ),
            RuntimeWarning,
            stacklevel=2,
        )
        _PRODUCT_CACHE[product_type] = stale
        return _copy_products(stale[1])
    finally:
        if task.done() and _REFRESH_TASKS.get(key) is task:
            _REFRESH_TASKS.pop(key, None)


async def search_products(
    *,
    symbol: str | None = None,
    product_type: ProductType | None = None,
    asset_class: str | None = None,
    exchange: str | None = None,
    query: str | None = None,
    client: CMEHttpClient | None = None,
) -> list[dict[str, Any]]:
    """Search the generated CME catalog."""
    if client is None:
        async with CMEHttpClient() as owned_client:
            return await search_products(
                symbol=symbol,
                product_type=product_type,
                asset_class=asset_class,
                exchange=exchange,
                query=query,
                client=owned_client,
            )
    types: tuple[ProductType, ...] = (
        (product_type,) if product_type else ("Futures", "Options")
    )
    catalogs = await asyncio.gather(
        *(fetch_product_catalog(value, client=client) for value in types)
    )
    products = [row for catalog in catalogs for row in catalog]

    if symbol:
        target = symbol.strip().upper()
        products = [
            row
            for row in products
            if target
            in {
                str(row.get("symbol", "")).upper(),
                *(
                    str(value).upper()
                    for value in row.get("codes", {}).values()
                    if value
                ),
            }
        ]
    if asset_class:
        products = [
            row
            for row in products
            if str(row.get("asset_class", "")).casefold() == asset_class.casefold()
        ]
    if exchange:
        products = [
            row
            for row in products
            if str(row.get("exchange", "")).casefold() == exchange.casefold()
        ]
    if query:
        target = query.casefold()
        products = [
            row
            for row in products
            if target in str(row.get("name", "")).casefold()
            or target in str(row.get("symbol", "")).casefold()
        ]

    return sorted(
        products,
        key=lambda row: (
            row.get("asset_class") or "",
            row.get("name") or "",
            row["product_id"],
        ),
    )


async def resolve_product(
    symbol: str,
    product_type: ProductType,
    *,
    client: CMEHttpClient | None = None,
) -> dict[str, Any] | None:
    """Resolve a CME symbol to the most liquid exact catalog match."""
    matches = await search_products(
        symbol=symbol,
        product_type=product_type,
        client=client,
    )
    if not matches:
        return None
    return max(
        matches,
        key=lambda row: (
            bool(row.get("globex_traded")),
            row.get("volume") or 0,
            row.get("open_interest") or 0,
        ),
    )


def _flatten_spec_value(value: Any) -> str | dict[str, Any] | list[Any] | None:
    """Recursively clean HTML embedded in specification payloads."""
    if isinstance(value, str):
        return _plain_text(value)
    if isinstance(value, list):
        return [
            cleaned
            for item in value
            if (cleaned := _flatten_spec_value(item)) is not None
        ]
    if isinstance(value, dict):
        return {
            key: cleaned
            for key, item in value.items()
            if (cleaned := _flatten_spec_value(item)) is not None
        }
    return value


async def fetch_contract_specifications(
    product_id: int,
    client: CMEHttpClient | None = None,
) -> dict[str, Any]:
    """Fetch and normalize the complete public specification for a CME product."""
    url = f"{helpers.BASE_URL}/CmeWS/mvc/ContractSpecs/List/productId/{product_id}"
    response = await helpers._get_json(url, client)
    if not isinstance(response, dict) or not (
        response.get("ProductID") or response.get("ProductName")
    ):
        raise CMERequestError(
            f"CME returned an invalid contract specification payload: {url}",
            url=url,
        )
    return {
        key: cleaned
        for key, value in response.items()
        if (cleaned := _flatten_spec_value(value)) is not None
    }


def clear_catalog_cache(*, include_disk: bool = False) -> None:
    """Clear the in-memory product catalog cache."""
    _PRODUCT_CACHE.clear()
    _REFRESH_TASKS.clear()
    if include_disk:
        for product_type in ("Futures", "Options"):
            path = _catalog_cache_path(product_type)
            if path is not None:
                with suppress(OSError):
                    path.unlink(missing_ok=True)
