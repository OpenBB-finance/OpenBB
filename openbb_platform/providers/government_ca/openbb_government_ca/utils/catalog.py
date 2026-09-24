"""Runtime reader for the shipped ``government_ca_cache.json.xz`` catalog.

Loads and LZMA-decompresses the catalog asset materialized at build time and
answers discovery/lookup queries against the in-memory curated tables. Performs
NO network calls on load, decompression, or lookup.
"""

from __future__ import annotations

import json
import lzma
from pathlib import Path

from openbb_core.app.model.abstract.error import OpenBBError

_CACHE_FILE = (
    Path(__file__).resolve().parents[1] / "assets" / "government_ca_cache.json.xz"
)


class CatalogUnavailableError(OpenBBError):
    """Raised when the catalog asset is missing, corrupt, or undecompressable."""


class CatalogReader:
    """Read the shipped catalog and answer discovery/lookup queries.

    Parameters
    ----------
    cache_file : Path, optional
        Path to the LZMA-compressed JSON catalog asset; defaults to the shipped
        ``government_ca_cache.json.xz``.

    Raises
    ------
    CatalogUnavailableError
        When the asset is missing, cannot be decompressed, or cannot be parsed.
    """

    def __init__(self, cache_file: Path = _CACHE_FILE) -> None:
        try:
            raw = cache_file.read_bytes()
            blob = json.loads(lzma.decompress(raw))
        except (OSError, lzma.LZMAError, json.JSONDecodeError) as exc:
            raise CatalogUnavailableError(
                f"catalog unavailable at {cache_file}: {exc}"
            ) from exc
        self._tables: dict[str, dict] = blob.get("tables", {})

    def indicators(self) -> list[dict]:
        """Return the curated discovery list (empty catalog yields ``[]``).

        Returns
        -------
        list[dict]
            One discovery projection per table: ``pid``, ``name_en``,
            ``name_fr``, ``frequency``, and the list of dimension ids.
        """
        return [
            {
                "pid": entry["pid"],
                "name_en": entry["name"]["en"],
                "name_fr": entry["name"]["fr"],
                "frequency": entry["frequency"],
                "dimensions": [dim["id"] for dim in entry["dimensions"]],
            }
            for entry in self._tables.values()
        ]

    def lookup(self, codr_pid: str) -> dict | None:
        """Return the ``Normalized_Table_Entry`` for a PID, or ``None``.

        Parameters
        ----------
        codr_pid : str
            The 8-digit CODR PID to resolve.

        Returns
        -------
        dict | None
            The matching entry, or ``None`` when the PID is absent. Never a
            network fetch.
        """
        return self._tables.get(codr_pid)
