"""Cache management mixin for ``GovernmentCaMetadata``.

Reads and writes the cache blob. Supports two on-disk formats:

- ``.xz``  (LZMA-compressed JSON) — the shipped cache, produced at
  build time by ``hatch_build.py``. Compact (~70% smaller than gzip
  for the kind of repetitive JSON we ship) but slower to write.
- ``.gz``  (gzip-compressed JSON) — the user cache, written at runtime
  when the user explicitly refreshes metadata. Faster to write, and
  small enough at our scale that the size penalty is irrelevant.

Both formats are auto-detected by magic bytes so the loader doesn't
need to know which file it's reading.
"""

from __future__ import annotations

import gzip
import json
import lzma
import warnings
from pathlib import Path

from openbb_government_ca.utils.metadata._constants import (
    _SHIPPED_CACHE_FILE,
    _USER_CACHE_FILE,
)
from openbb_government_ca.utils.metadata._typing import _MixinBase

_XZ_MAGIC = b"\xfd7zXZ\x00"
_GZ_MAGIC = b"\x1f\x8b"


class CacheMixin(_MixinBase):
    """Methods for reading, writing, and applying metadata cache blobs."""

    @staticmethod
    def _read_cache_file(path: Path) -> dict | None:
        """Read and return a cache blob, or ``None`` on any failure.

        Auto-detects LZMA vs gzip by magic bytes; falls back to plain
        JSON if neither matches (useful for debugging — drop a plain
        JSON file at the path and the loader will pick it up).
        """
        try:
            if not path.exists():
                return None
            raw = path.read_bytes()
            if raw[:6] == _XZ_MAGIC:
                data = lzma.decompress(raw)
            elif raw[:2] == _GZ_MAGIC:
                data = gzip.decompress(raw)
            else:
                data = raw
            return json.loads(data.decode("utf-8"))
        except Exception:  # noqa: BLE001
            return None

    def _apply_blob(self, blob: dict) -> None:
        """Merge a cache *blob* into the current metadata state.

        The blob schema is::

            {
              "generated_at": "2026-06-28T04:17:00Z",
              "source": "build-hook",
              "boc": {
                "series": { ... },
                "groups": { ... },
              },
              "statscan": {
                "products": { ... },
              },
            }

        Partial blobs are tolerated: missing sub-maps are filled in
        with empty defaults so downstream callers can always rely on
        ``self.boc["series"]`` / ``self.boc["groups"]`` /
        ``self.statscan["products"]`` being present.
        """
        self.blob = blob
        raw_boc = blob.get("boc") or {}
        raw_statscan = blob.get("statscan") or {}
        # Always materialise the canonical sub-maps so callers never
        # have to defensively check for their existence.
        self._boc = {
            "series": raw_boc.get("series") or {},
            "groups": raw_boc.get("groups") or {},
        }
        # Preserve any extra keys the generator may add later (e.g.
        # ``valet_url``, ``note``) without clobbering them.
        for k, v in raw_boc.items():
            if k not in self._boc:
                self._boc[k] = v
        self._statscan = {
            "indicators": raw_statscan.get("indicators") or [],
            "geo_lookup": raw_statscan.get("geo_lookup") or {},
        }
        for k, v in raw_statscan.items():
            if k not in self._statscan:
                self._statscan[k] = v
        self._generated_at = blob.get("generated_at", "")
        self._source = blob.get("source", "unknown")

    def _load_from_cache(self) -> bool:
        """Load metadata from the shipped cache, then layer user cache on top.

        Returns ``True`` if at least one cache was loaded successfully.
        Warns (but does not raise) if no cache is available — the
        fetchers will then attempt to hit upstream APIs directly,
        which is the documented V5 behavior.
        """
        loaded = False
        shipped = self._read_cache_file(_SHIPPED_CACHE_FILE)
        if shipped:
            self._apply_blob(shipped)
            loaded = True
        user = self._read_cache_file(_USER_CACHE_FILE())
        if user:
            # User cache takes precedence — it's the most recent.
            self._apply_blob(user)
            loaded = True
        if not loaded:
            warnings.warn(
                "No Government of Canada metadata cache found; "
                "fetchers will hit upstream APIs directly. "
                "Reinstall the package or run "
                "`generate-government-ca-cache` to populate the cache.",
                stacklevel=2,
            )
        return loaded

    def _save_user_cache(self) -> None:
        """Persist current metadata to the user-writable cache (gzip+JSON)."""
        try:
            cache_file = _USER_CACHE_FILE()
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            raw = json.dumps(self.blob, separators=(",", ":")).encode("utf-8")
            cache_file.write_bytes(gzip.compress(raw, compresslevel=6))
        except Exception:  # noqa: BLE001
            warnings.warn(
                "Failed to persist Government of Canada metadata cache.",
                stacklevel=2,
            )
