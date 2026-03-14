"""OECD Progressive Query Helper.

Matches the interface of ImfParamsBuilder for consistent cross-provider
behaviour.  All live constraint checking is delegated to
OecdMetadata.fetch_availability().
"""

# pylint: disable=W0212

from __future__ import annotations

from openbb_core.app.model.abstract.error import OpenBBError


class OecdParamsBuilder:
    """Progressive dimension selection with cascading availability checks.

    Walks the DSD dimensions in order.  At each step, queries the OECD
    availability endpoint so that only values valid given prior
    selections are returned.  When a dimension is set, all *downstream*
    selections (later in DSD order) are cleared — they may now be
    invalid.

    Examples
    --------
    >>> from openbb_oecd.utils.progressive_helper import OecdParamsBuilder
    >>> builder = OecdParamsBuilder("DF_PRICES_ALL")
    >>> builder.get_dimensions_in_order()
    ['REF_AREA', 'FREQ', 'METHODOLOGY', 'MEASURE', ...]
    >>> builder.set_dimension(("REF_AREA", "USA"))
    {'REF_AREA': 'USA', 'FREQ': None, ...}
    >>> builder.get_options_for_dimension("FREQ")
    [{'label': 'Annual', 'value': 'A'}, ...]
    """

    def __init__(self, dataflow_id: str) -> None:
        """Initialize the OecdParamsBuilder.

        Parameters
        ----------
        dataflow_id : str
            Short or full OECD dataflow ID (e.g. ``"DF_PRICES_ALL"``).

        Raises
        ------
        OpenBBError
            If the dataflow cannot be resolved.
        """
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.metadata import OecdMetadata

        self._metadata = OecdMetadata()

        # Resolve and ensure the DSD is loaded.
        self._full_id = self._metadata._resolve_dataflow_id(dataflow_id)
        self._metadata._ensure_structure(self._full_id)

        self.dataflow_id = dataflow_id

        # Dimension IDs in DSD position order (excludes TIME_PERIOD).
        self._dimensions: list[str] = self._metadata.get_dimension_order(self._full_id)
        self.current_dimension: str | None = (
            self._dimensions[0] if self._dimensions else None
        )

        # Current selections: ``None`` = not yet selected.
        self._selections: dict[str, str | None] = {
            dim: None for dim in self._dimensions
        }

        # Availability cache keyed by frozen pinned state.
        self._avail_cache: dict[frozenset, dict[str, list[str]]] = {}

        # Codelist label caches (dim_id → {code: label}).
        self._labels: dict[str, dict[str, str]] = {}


    def get_dimensions_in_order(self) -> list[str]:
        """Return dimension IDs sorted by DSD position, excluding TIME_PERIOD."""
        return list(self._dimensions)

    def get_next_dimension_to_select(self) -> str | None:
        """Return the first dimension where no selection has been made.

        Returns
        -------
        str or None
            Dimension ID, or ``None`` if all dimensions have been selected.
        """
        for dim in self._dimensions:
            if self._selections[dim] is None:
                return dim
        return None

    def set_dimension(self, dimension: tuple[str, str]) -> dict[str, str | None]:
        """Pin *dimension* to *value* and **clear all downstream** selections.

        Parameters
        ----------
        dimension : tuple[str, str]
            ``(dimension_id, value)`` to set.

        Returns
        -------
        dict
            Updated selections after setting the dimension.

        Raises
        ------
        KeyError
            If *dimension_id* is not a valid dimension of this dataflow.
        """
        dim_id, value = dimension

        if dim_id not in self._selections:
            raise KeyError(
                f"Dimension '{dim_id}' not valid for dataflow '{self.dataflow_id}'. "
                f"Valid dimensions: {list(self._selections.keys())}"
            )

        self._selections[dim_id] = value

        # Clear everything *after* this dimension in DSD order.
        found = False
        for d in self._dimensions:
            if found:
                self._selections[d] = None
            if d == dim_id:
                found = True

        # Invalidate stale cache entries.
        self._avail_cache.clear()
        self.current_dimension = self.get_next_dimension_to_select()

        return dict(self._selections)

    def get_options_for_dimension(
        self, dimension_id: str | None = None
    ) -> list[dict[str, str]]:
        """Return available values for a dimension given the current selections.

        Parameters
        ----------
        dimension_id : str, optional
            The dimension to query.  Defaults to the next unselected
            dimension.

        Returns
        -------
        list[dict]
            ``[{label, value}, ...]`` reflecting cascading constraints.
        """
        dimension_id = dimension_id or self.get_next_dimension_to_select()
        if not dimension_id:
            return []
        if dimension_id not in self._selections:
            raise ValueError(
                f"Dimension '{dimension_id}' not found for dataflow '{self.dataflow_id}'."
            )

        avail = self._fetch_current_availability()
        codes = avail.get(dimension_id, [])
        labels = self._get_labels(dimension_id)

        return [{"label": labels.get(code, code), "value": code} for code in codes]

    def get_dimensions(self) -> dict[str, str | None]:
        """Return the current selections dictionary."""
        return dict(self._selections)

    @property
    def dimensions(self) -> list[str]:
        """Return dimension IDs in DSD order."""
        return list(self._dimensions)

    @property
    def pinned(self) -> dict[str, str]:
        """Return currently pinned (non-None) selections."""
        return {k: v for k, v in self._selections.items() if v is not None}

    def available(self, dim_id: str) -> list[dict[str, str]]:
        """Alias for :meth:`get_options_for_dimension`."""
        return self.get_options_for_dimension(dim_id)

    def available_values(self, dim_id: str) -> list[str]:
        """Return just the available codes for *dim_id* (no labels)."""
        if dim_id not in self._selections:
            raise OpenBBError(
                f"'{dim_id}' is not a dimension of '{self.dataflow_id}'. Dimensions: {self._dimensions}"
            )
        avail = self._fetch_current_availability()
        return avail.get(dim_id, [])

    def set(self, dim_id: str, value: str) -> OecdParamsBuilder:
        """Pin a dimension (chainable).  Validates against current availability.

        Parameters
        ----------
        dim_id : str
            Dimension ID.
        value : str
            Code or ``+``-separated codes.

        Returns
        -------
        OecdParamsBuilder
            Self, for chaining.
        """
        if dim_id not in self._selections:
            raise OpenBBError(
                f"'{dim_id}' is not a dimension of '{self.dataflow_id}'. Dimensions: {self._dimensions}"
            )

        # Validate each code.
        avail = self._fetch_current_availability()
        valid_codes = set(avail.get(dim_id, []))
        codes = [c.strip() for c in value.split("+") if c.strip()]
        invalid = [c for c in codes if c not in valid_codes]

        if invalid:
            labels = self._get_labels(dim_id)
            sample = [f"{c} ({labels.get(c, c)})" for c in sorted(valid_codes)[:20]]
            raise OpenBBError(
                f"Invalid value(s) {invalid} for '{dim_id}' "
                f"given current selections {self.pinned}. "
                f"Available ({len(valid_codes)}): {sample}"
                + (" …" if len(valid_codes) > 20 else "")
            )

        self._selections[dim_id] = value

        # Clear downstream selections (IMF behaviour).
        found = False
        for d in self._dimensions:
            if found:
                self._selections[d] = None
            if d == dim_id:
                found = True

        # Keep only the cache entry that matches the new state.
        key = self._cache_key()
        self._avail_cache = {k: v for k, v in self._avail_cache.items() if k == key}

        return self

    def unset(self, dim_id: str) -> OecdParamsBuilder:
        """Remove the pin for *dim_id*.  Returns self for chaining."""
        if dim_id in self._selections:
            self._selections[dim_id] = None
        self._avail_cache.clear()
        return self

    def reset(self) -> OecdParamsBuilder:
        """Clear all pins and caches.  Returns self for chaining."""
        for d in self._selections:
            self._selections[d] = None
        self._avail_cache.clear()
        return self

    def describe(self) -> list[dict]:
        """Full description of every dimension and its current state."""
        avail = self._fetch_current_availability()
        table_params = self._metadata.get_table_parameters(self._full_id)
        result: list[dict] = []

        for dim_id in self._dimensions:
            info = table_params.get(dim_id, {})
            codes = avail.get(dim_id, [])
            labels = self._get_labels(dim_id)
            result.append(
                {
                    "id": dim_id,
                    "name": info.get("name", dim_id),
                    "position": info.get("position", -1),
                    "role": info.get("role", ""),
                    "pinned": self._selections.get(dim_id),
                    "available_count": len(codes),
                    "available": [
                        {"value": c, "label": labels.get(c, c)} for c in codes
                    ],
                }
            )

        return result

    def summary(self) -> list[dict]:
        """Compact summary: id, name, role, pinned value, available count."""
        avail = self._fetch_current_availability()
        table_params = self._metadata.get_table_parameters(self._full_id)
        result: list[dict] = []

        for dim_id in self._dimensions:
            info = table_params.get(dim_id, {})
            codes = avail.get(dim_id, [])
            result.append(
                {
                    "id": dim_id,
                    "name": info.get("name", dim_id),
                    "role": info.get("role", ""),
                    "pinned": self._selections.get(dim_id),
                    "available_count": len(codes),
                }
            )

        return result

    def build(self) -> str:
        """Build the v2 dimension filter string from current pins.

        Unpinned dimensions default to ``*`` (wildcard).
        TIME_PERIOD is appended as the final ``*``.
        """
        parts: list[str] = []
        for dim_id in self._dimensions:
            parts.append(self._selections.get(dim_id) or "*")
        # TIME_PERIOD is always the last position as wildcard.
        parts.append("*")
        return ".".join(parts)

    def build_url(
        self,
        last_n: int | None = None,
        first_n: int | None = None,
    ) -> str:
        """Build a complete SDMX v2 data URL from the current state."""
        return self._metadata.build_data_url(
            self._full_id,
            dimension_filter=self.build(),
            last_n=last_n,
            first_n=first_n,
        )

    def fetch(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict:
        """Fetch data based on the current selections.

        Parameters
        ----------
        start_date, end_date : str, optional
            Date bounds.

        Returns
        -------
        dict
            ``{data: [...], metadata: {...}}``.
        """
        # pylint: disable=import-outside-toplevel
        from openbb_oecd.utils.query_builder import OecdQueryBuilder

        qb = OecdQueryBuilder()
        return qb.fetch_data(
            dataflow=self.dataflow_id,
            start_date=start_date,
            end_date=end_date,
            **self.pinned,
        )

    def _cache_key(self) -> frozenset:
        """Hashable key for the current pinned state."""
        return frozenset((k, v) for k, v in self._selections.items() if v is not None)

    def _fetch_current_availability(self) -> dict[str, list[str]]:
        """Fetch (or return cached) availability for the current pinned state."""
        key = self._cache_key()
        if key not in self._avail_cache:
            self._avail_cache[key] = self._metadata.fetch_availability(
                self._full_id, self.pinned
            )
        return self._avail_cache[key]

    def _get_labels(self, dim_id: str) -> dict[str, str]:
        """Get codelist labels for a dimension, caching them."""
        if dim_id not in self._labels:
            self._labels[dim_id] = self._metadata.get_codelist_for_dimension(
                self._full_id, dim_id
            )
        return self._labels[dim_id]

    def __repr__(self) -> str:  # noqa: D105
        return f"OecdParamsBuilder({self.dataflow_id}, pinned={self.pinned}, dims={self._dimensions})"
