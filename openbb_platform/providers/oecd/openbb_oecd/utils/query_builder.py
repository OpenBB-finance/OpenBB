"""OECD Query Builder for constructing and executing SDMX v2 data queries.

Shared data-fetching engine that all OECD fetchers delegate to.
Uses OecdMetadata for structural metadata (DSD-driven dimension ordering,
codelist lookups, availability constraints) and SDMX-CSV v2 for data retrieval.
"""

# pylint: disable=C0302,R0911,R0912,R0913,R0914,R0915,R0917,R1702,W0212
# flake8: noqa: PLR0911,PLR0912,PLR0913,PLR0917

import warnings
from io import StringIO
from typing import TYPE_CHECKING, Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_oecd.utils.metadata import OecdMetadata
from openbb_oecd.utils.progressive_helper import OecdParamsBuilder
from pandas.api.types import is_string_dtype

if TYPE_CHECKING:
    from pandas import DataFrame  # type: ignore[import-untyped]


class OecdQueryBuilder:
    """Build and execute OECD SDMX v2 data queries."""

    def __init__(self):
        """Initialize the query builder with the metadata singleton."""
        self.metadata = OecdMetadata()

    def build_url(
        self,
        dataflow: str,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Build an SDMX v2 data URL for *dataflow* with dimension kwargs.

        Parameters
        ----------
        dataflow : str
            Dataflow short ID ("DF_PRICES_ALL") or full v2 ID.
        start_date : str | None
            ISO date string ("YYYY-MM-DD" or "YYYY").
            Not natively supported in v2 — mapped to startPeriod.
        end_date : str | None
            ISO date string.  Mapped to endPeriod.
        limit : int | None
            lastNObservations for the most recent N data points.
        **kwargs
            Dimension values keyed by dimension ID (case-sensitive).
            Use "+"-separated strings for multi-select.
            Omitted dimensions default to "*" (wildcard).

        Returns
        -------
        str
            A fully-qualified SDMX v2 data URL.
        """
        # Resolve dimension kwargs to a filter string using DSD ordering.
        dimension_filter = self._build_dimension_filter(dataflow, **kwargs)

        # When time constraints are present, detail=dataonly must NOT be
        # used — the OECD API silently ignores c[TIME_PERIOD] filters
        # when detail=dataonly is set.
        has_time_constraint = bool(start_date or end_date)

        # Build the base URL via metadata.
        # When date constraints are present, omit lastNObservations —
        # the OECD API applies lastN *before* c[TIME_PERIOD] filtering,
        # which can result in 404 when the latest obs falls outside the
        # requested range.
        url = self.metadata.build_data_url(
            dataflow,
            dimension_filter=dimension_filter,
            last_n=limit if not has_time_constraint else None,
            detail="full" if has_time_constraint else "dataonly",
        )

        # v2 uses c[TIME_PERIOD] constraints (not startPeriod/endPeriod).
        # Both ge: and le: must be in a SINGLE c[TIME_PERIOD] param,
        # comma-separated.  Duplicate query params are silently ignored.
        _time_parts: list[str] = []
        if start_date:
            _time_parts.append(f"ge:{_format_period(start_date)}")
        if end_date:
            _time_parts.append(f"le:{_format_period(end_date)}")
        if _time_parts:
            url += f"&c[TIME_PERIOD]={','.join(_time_parts)}"

        return url

    def _build_dimension_filter(self, dataflow: str, **kwargs: Any) -> str:
        """Build a dot-separated dimension filter from keyword args.

        Delegates to OecdMetadata.build_dimension_filter which includes
        ALL dimensions (including TIME_PERIOD) in DSD order — required by
        the v2 API.

        Performs case-insensitive matching of kwarg keys to DSD dimension
        IDs, so callers can use ref_area="USA" or REF_AREA="USA"
        interchangeably.
        """
        # Get the DSD dimension order for case-insensitive matching.
        dim_order = self.metadata.get_dimension_order(dataflow)
        dim_id_map = {d.lower(): d for d in dim_order}

        # Normalise kwargs to canonical dimension IDs.
        normalised: dict[str, str] = {}
        for key, value in kwargs.items():
            matched = dim_id_map.get(key.lower())
            if matched:
                normalised[matched] = str(value) if value is not None else "*"

        # Delegate to metadata which includes TIME_PERIOD in the filter.
        return self.metadata.build_dimension_filter(dataflow, **normalised)

    def validate_dimension_constraints(self, dataflow: str, **kwargs: Any) -> None:
        """Validate dimension parameters against the OECD availability API.

        Uses progressive constraint checking: dimensions are validated in
        DSD order, and each step narrows the available values for
        subsequent dimensions.

        Parameters
        ----------
        dataflow : str
            Dataflow short ID or full v2 ID.
        **kwargs
            Dimension parameters to validate.  Non-dimension kwargs
            (start_date, end_date, limit) are ignored.

        Raises
        ------
        ValueError
            If any dimension value is not available given prior selections.
        """
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.abstract.warning import OpenBBWarning

        # Filter kwargs to only dimension IDs.
        dim_order = self.metadata.get_dimension_order(dataflow)
        dim_id_map = {d.lower(): d for d in dim_order}
        non_dimension_keys = {"start_date", "end_date", "limit"}

        dim_kwargs: dict[str, str] = {}
        for key, value in kwargs.items():
            if key in non_dimension_keys:
                continue
            matched = dim_id_map.get(key.lower())
            if matched and value is not None:
                dim_kwargs[matched] = str(value)

        if not dim_kwargs:
            return

        try:
            qb = OecdParamsBuilder(dataflow)
        except Exception as exc:  # noqa: BLE001
            warnings.warn(
                f"Could not initialise query builder for dataflow '{dataflow}': {exc}",
                OpenBBWarning,
                stacklevel=2,
            )
            return

        for dim_id in dim_order:
            if dim_id not in dim_kwargs:
                continue

            user_value = dim_kwargs[dim_id]

            # Parse multi-select.
            if "+" in user_value:
                user_values = [v.strip() for v in user_value.split("+")]
            elif "," in user_value:
                user_values = [v.strip() for v in user_value.split(",")]
            else:
                user_values = [user_value]

            user_values = [v for v in user_values if v and v != "*"]
            if not user_values:
                continue

            is_multi = len(user_values) > 1

            # Get available options given current single-value pins.
            # If the availability fetch itself fails, warn and skip this dimension.
            try:
                available_options = qb.available(dim_id)
            except Exception as exc:  # noqa: BLE001
                warnings.warn(
                    f"Could not fetch availability for dimension '{dim_id}' of dataflow '{dataflow}': {exc}",
                    OpenBBWarning,
                    stacklevel=2,
                )
                # Still pin if it's a single value so downstream dims are constrained.
                if not is_multi:
                    qb.set_dimension((dim_id, user_values[0]))
                continue

            available_codes = {opt["value"] for opt in available_options}

            invalid = [v for v in user_values if v not in available_codes]
            if invalid:
                prior = {
                    d: dim_kwargs[d]
                    for d in dim_order
                    if d in dim_kwargs and dim_order.index(d) < dim_order.index(dim_id)
                }
                # Build a compact list of available options with labels.
                avail_display = [
                    (
                        f"{opt['value']} ({opt['label']})"
                        if opt.get("label") and opt["label"] != opt["value"]
                        else opt["value"]
                    )
                    for opt in sorted(available_options, key=lambda x: x["value"])
                ]
                raise ValueError(
                    f"Invalid value(s) for dimension '{dim_id}': {invalid}. "
                    + (f"Given prior selections {prior}, " if prior else "")
                    + f"Available options ({len(avail_display)}): "
                    + ", ".join(avail_display)
                )

            # Only pin single-value selections for cascading constraint propagation.
            # Multi-select values break the availability API endpoint, so we skip
            # pinning them — they were valid individually; downstream dims will use
            # the already-pinned single-value context.
            if not is_multi:
                qb.set_dimension((dim_id, user_values[0]))

    def fetch_data(
        self,
        dataflow: str,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
        _skip_validation: bool = False,
        **kwargs: Any,
    ) -> dict:
        """Fetch data from the OECD SDMX v2 API.

        This is the main entry point for all refactored models.

        Parameters
        ----------
        dataflow : str
            Dataflow short ID ("DF_PRICES_ALL") or full v2 ID.
        start_date, end_date : str | None
            Date bounds (ISO format).
        limit : int | None
            lastNObservations to limit time series depth.
        _skip_validation : bool
            Skip constraint validation (when caller already validated).
        **kwargs
            Dimension parameters keyed by dimension ID.

        Returns
        -------
        dict
            {"data": list[dict], "metadata": dict}

            Each row in data contains:
            - One key per dimension ID (the **code**).
            - One key per {dim_id}_label (the human-readable label).
            - TIME_PERIOD — the time period string ("2024", "2024-Q3", etc.).
            - OBS_VALUE — the numeric observation value (float | None).

            metadata contains:
            - dataflow_id, dataflow_name, url, row_count.
        """
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.errors import EmptyDataError
        from pandas import read_csv, to_numeric

        # Validate constraints (unless caller opted out).
        if not _skip_validation:
            self.validate_dimension_constraints(dataflow, **kwargs)

        url = self.build_url(dataflow, start_date, end_date, limit, **kwargs)

        # Fetch SDMX-CSV v2 with labels=both.
        headers = {
            "Accept": "application/vnd.sdmx.data+csv; version=2.0.0; labels=both",
            "User-Agent": "OpenBB/1.0",
        }

        # Attempt the request; if it fails with 404 and there are
        # multi-value dimensions (e.g. "USA+DEU"), fall back to
        # individual requests per value and merge results.
        text = self._fetch_with_multi_value_fallback(
            url,
            headers,
            dataflow,
            start_date,
            end_date,
            limit,
            kwargs,
        )

        # Parse the CSV.
        try:
            df = read_csv(StringIO(text))
        except Exception as exc:
            raise OpenBBError(
                f"Failed to parse OECD CSV response: {exc}\nURL: {url}"
            ) from exc

        if df.empty:
            raise OpenBBError(
                EmptyDataError(f"No data rows for dataflow '{dataflow}'. URL: {url}")
            )

        # Split "code: label" columns into separate code and label columns.
        df = self._split_label_columns(df, dataflow)

        # Ensure OBS_VALUE is numeric.
        if "OBS_VALUE" in df.columns:
            df["OBS_VALUE"] = to_numeric(df["OBS_VALUE"], errors="coerce")

        # Build result metadata.
        df_meta = self.metadata.dataflows.get(
            self.metadata._resolve_dataflow_id(dataflow), {}
        )
        metadata = {
            "dataflow_id": dataflow,
            "dataflow_name": df_meta.get("name", dataflow),
            "url": url,
            "row_count": len(df),
        }

        # Convert NaN → None so downstream JSON serialization doesn't break.
        records = df.where(df.notna(), other=None).to_dict(orient="records")

        return {"data": records, "metadata": metadata}

    def _fetch_with_multi_value_fallback(
        self,
        url: str,
        headers: dict,
        dataflow: str,
        start_date: str | None,
        end_date: str | None,
        limit: int | None,
        dim_kwargs: dict[str, Any],
    ) -> str:
        """Fetch CSV text, falling back to per-value requests if multi-value fails.

        The OECD SDMX v2 API doesn't reliably support the ``+``
        multi-value separator in the path-based dimension key.
        When a 404 is received and at least one dimension contains ``+``,
        we split the first such dimension into individual requests
        and concatenate the CSV results.
        """
        from requests.exceptions import HTTPError  # type: ignore[import-untyped]

        try:
            response = _make_request(url, headers=headers, timeout=120)
            text = response.text
            if text and text.strip():
                return text
            raise OpenBBError(
                f"Empty response from OECD for dataflow '{dataflow}'. URL: {url}"
            )
        except (HTTPError, OpenBBError) as exc:
            # Identify dimensions with multi-value (contains +).
            multi_dims = {
                k: v for k, v in dim_kwargs.items() if isinstance(v, str) and "+" in v
            }
            if not multi_dims:
                raise OpenBBError(
                    f"OECD data request failed: {exc}\nURL: {url}"
                ) from exc

            # Pick the first multi-value dimension to split on.
            split_dim = next(iter(multi_dims))
            values = multi_dims[split_dim].split("+")

            csv_parts: list[str] = []
            csv_header: str | None = None
            for val in values:
                single_kwargs = {**dim_kwargs, split_dim: val}
                single_url = self.build_url(
                    dataflow,
                    start_date,
                    end_date,
                    limit,
                    **single_kwargs,
                )
                try:
                    resp = _make_request(single_url, headers=headers, timeout=120)
                except Exception:  # noqa: BLE001, S112
                    continue
                part = resp.text
                if not part or not part.strip():
                    continue
                lines = part.strip().split("\n")
                if csv_header is None:
                    csv_header = lines[0]
                    csv_parts.append(part.strip())
                else:
                    # Skip the header line for subsequent parts.
                    csv_parts.append("\n".join(lines[1:]))

            if not csv_parts:
                raise OpenBBError(
                    f"OECD data request failed for all values of '{split_dim}': {values}\nURL: {url}"
                ) from exc

            return "\n".join(csv_parts)

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    def _split_label_columns(self, df: "DataFrame", dataflow: str) -> "DataFrame":
        """Process SDMX-CSV v2 labels=both columns.

        The labels=both format gives column headers like
        "MEASURE: Measure" and cell values like
        "B1GQ: Gross domestic product".

        This method renames columns from "DIM: Label" to "DIM",
        splits cell values "code: label" into DIM (code) and
        DIM_label (label), and leaves TIME_PERIOD / OBS_VALUE as-is.
        """

        # Build a map of original column names → clean dimension IDs.
        rename_map: dict[str, str] = {}

        for col in df.columns:
            if ": " in col:
                dim_id = col.split(":")[0].strip()
                rename_map[col] = dim_id
            else:
                rename_map[col] = col

        df = df.rename(columns=rename_map)

        # Identify dimension columns that contain "code: label" values.
        # Exclude TIME_PERIOD, OBS_VALUE, and any purely numeric columns.
        skip_cols = {
            "TIME_PERIOD",
            "OBS_VALUE",
            "DATAFLOW",
            "STRUCTURE",
            "STRUCTURE_ID",
            "ACTION",
        }
        dim_cols = [
            c for c in df.columns if c not in skip_cols and is_string_dtype(df[c])
        ]

        for col in dim_cols:
            # Check if values actually contain ": " separator.
            sample = df[col].dropna().head(10)
            if sample.empty:
                continue

            has_labels = sample.str.contains(": ", regex=False).any()

            if has_labels:
                # Split into code and label.
                split = df[col].str.split(": ", n=1, expand=True)
                df[col] = split[0].str.strip()
                if split.shape[1] > 1:
                    df[f"{col}_label"] = split[1].str.strip()
                else:
                    df[f"{col}_label"] = df[col]
            else:
                # No labels embedded — try to resolve from codelist.
                cl = self.metadata.get_codelist_for_dimension(dataflow, col)
                if cl:
                    df[f"{col}_label"] = df[col].map(cl).fillna(df[col])

        return df

    def get_translation_maps(self, dataflow: str) -> dict[str, dict[str, str]]:
        """Return code-to-label maps for all dimensions.

        Returns
        -------
        dict[str, dict[str, str]]
            {dim_id: {code: label, ...}} for all dimensions.
        """
        params = self.metadata.get_dataflow_parameters(dataflow)
        return {
            dim_id: {opt["value"]: opt["label"] for opt in options}
            for dim_id, options in params.items()
        }

    def get_country_dimension(self, dataflow: str) -> str | None:
        """Return the dimension ID used for country/reference area, or None."""
        classification = self.metadata.classify_dimensions(dataflow)
        country_dims = classification.get("country", [])
        return country_dims[0]["id"] if country_dims else None

    def get_frequency_dimension(self, dataflow: str) -> str | None:
        """Return the dimension ID used for frequency, or None."""
        classification = self.metadata.classify_dimensions(dataflow)
        freq_dims = classification.get("freq", [])
        return freq_dims[0]["id"] if freq_dims else None

    def list_tables(
        self, query: str | None = None, topic: str | None = None
    ) -> list[dict]:
        """List all OECD tables (every dataflow is a table).

        Parameters
        ----------
        query : str, optional
            Keyword search on table name / dataflow ID / topic.
        topic : str, optional
            Topic code filter (e.g. "ECO", "HEA").

        Returns
        -------
        list[dict]
            [{table_id, name, topic, subtopic, dataflow_id}, ...]
        """
        return self.metadata.list_tables(query=query, topic=topic)

    def get_table(self, table_id: str) -> dict:
        """Get full metadata for a table: name, dimensions, allowed values.

        Parameters
        ----------
        table_id : str
            Dataflow short ID (e.g. "DF_T725R_Q") or full ID.

        Returns
        -------
        dict
            {'dataflow_id', 'short_id', 'name', 'description', 'dimensions', ...}
        """
        return self.metadata.get_table(table_id)


def _make_request(url: str, headers: dict | None = None, timeout: int = 30) -> Any:
    """HTTP GET with raw URL support (OECD requires un-encoded brackets)."""
    # pylint: disable=import-outside-toplevel
    import time as _time

    import requests as _requests  # type: ignore[import-untyped]

    # Use a prepared request so that brackets in ``c[TIME_PERIOD]`` are
    # sent as-is instead of being percent-encoded to ``%5B`` / ``%5D``
    # which the OECD SDMX v2 API rejects with a 404.
    max_retries = 5
    for attempt in range(max_retries):
        req = _requests.Request("GET", url, headers=headers or {})
        prepared = req.prepare()
        prepared.url = url  # override — keep raw brackets

        sess = _requests.Session()
        resp = sess.send(prepared, timeout=timeout)

        if resp.status_code == 429 and attempt < max_retries - 1:
            retry_after = int(
                resp.headers.get("Retry-After", 15 * (attempt + 1))
            )
            _time.sleep(min(max(retry_after, 15), 90))
            continue

        resp.raise_for_status()
        return resp

    # Should not reach here, but just in case:
    resp.raise_for_status()
    return resp


def _format_period(date_str: str) -> str:
    """Normalise a date string to SDMX period format.

    Parameters
    ----------
    date_str : str
        Date in "YYYY-MM-DD", "YYYY-MM", or "YYYY" format.

    Returns
    -------
    str
        Period string suitable for startPeriod/endPeriod.
    """
    if not date_str:
        return date_str

    s = str(date_str)
    parts = s.split("-")

    if len(parts) == 3:
        return f"{parts[0]}-{parts[1]}"

    return s


def parse_time_period(time_str: str) -> str:
    """Convert SDMX time period strings to standardised date strings.

    Parameters
    ----------
    time_str : str
        SDMX time period (e.g. "2024", "2024-Q3",
        "2024-06", "2024-03-15").

    Returns
    -------
    str
        ISO date string ("YYYY-MM-DD").  Returns the original
        string if the format is unrecognised.
    """
    if not time_str:
        return time_str

    s = str(time_str).strip()

    # Daily: already YYYY-MM-DD
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        return s

    # Quarterly: YYYY-QN (must check before monthly since both are len 7)
    if "Q" in s:
        parts = s.split("-Q")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            year = parts[0]
            quarter = int(parts[1])
            month = (quarter - 1) * 3 + 1
            return f"{year}-{month:02d}-01"

    # Monthly: YYYY-MM
    if len(s) == 7 and s[4] == "-":
        return f"{s}-01"

    # Annual: YYYY
    if len(s) == 4 and s.isdigit():
        return f"{s}-01-01"

    return s
