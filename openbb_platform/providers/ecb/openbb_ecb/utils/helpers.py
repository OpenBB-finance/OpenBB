"""ECB SDMX-JSON parsing and shared helpers."""

from __future__ import annotations

import calendar
from datetime import date


def parse_sdmx_period(period: str, start: str | None = None) -> str:
    """Normalize an SDMX TIME_PERIOD to an ISO ``YYYY-MM-DD`` string.

    Prefers the observation's ``start`` timestamp when the JSON provides it
    (exact for every frequency). Otherwise derives the period-*start* date
    from the period id, supporting ``YYYY``, ``YYYY-MM``, ``YYYY-Qn``,
    ``YYYY-Sn``, ``YYYY-Wnn`` and ``YYYY-MM-DD``.
    """
    if start:
        return start[:10]
    if not period:
        return period
    try:
        if "-Q" in period:
            year, q = period.split("-Q")
            return date(int(year), {1: 1, 2: 4, 3: 7, 4: 10}[int(q)], 1).isoformat()
        if "-S" in period:
            year, s = period.split("-S")
            return date(int(year), 1 if int(s) == 1 else 7, 1).isoformat()
        if "-W" in period:
            year, week = period.split("-W")
            return date.fromisocalendar(int(year), int(week), 1).isoformat()
        parts = period.split("-")
        if len(parts) == 1 and parts[0].isdigit():
            return date(int(parts[0]), 1, 1).isoformat()
        if len(parts) == 2:
            return date(int(parts[0]), int(parts[1]), 1).isoformat()
    except (ValueError, KeyError):
        return period
    return period


def period_end(period: str, end: str | None = None) -> str:
    """Return the period-*ending* ISO date for an SDMX TIME_PERIOD."""
    if end:
        return end[:10]
    if not period:
        return period
    try:
        if "-Q" in period:
            year, q = period.split("-Q")
            month = {1: 3, 2: 6, 3: 9, 4: 12}[int(q)]
            return date(
                int(year), month, calendar.monthrange(int(year), month)[1]
            ).isoformat()
        parts = period.split("-")
        if len(parts) == 1 and parts[0].isdigit():
            return date(int(parts[0]), 12, 31).isoformat()
        if len(parts) == 2 and "W" not in period and "S" not in period:
            y, m = int(parts[0]), int(parts[1])
            return date(y, m, calendar.monthrange(y, m)[1]).isoformat()
    except (ValueError, KeyError):
        return period
    return parse_sdmx_period(period)


def parse_series_keys(message: dict) -> list[dict]:
    """Flatten a ``serieskeysonly`` SDMX-JSON message into one record per series.

    Each record carries every series dimension (``<DIM>`` = code,
    ``<DIM>__label`` = name), the dot-joined ``series_key``, and a human
    ``name`` built from the dimension labels. There are no observations.
    """
    datasets = message.get("dataSets") or []
    if not datasets:
        return []
    series_dims = message.get("structure", {}).get("dimensions", {}).get("series", [])
    rows: list[dict] = []
    for dataset in datasets:
        for series_key in dataset.get("series", {}):
            record: dict = {}
            codes: list[str] = []
            labels: list[str] = []
            for pos, raw_idx in enumerate(series_key.split(":") if series_key else []):
                if pos >= len(series_dims):
                    break
                dim = series_dims[pos]
                values = dim.get("values", [])
                idx = int(raw_idx)
                item = values[idx] if 0 <= idx < len(values) else {}
                if not isinstance(item, dict):
                    item = {"id": item}
                code, label = item.get("id"), item.get("name")
                record[dim.get("id")] = code
                record[f"{dim.get('id')}__label"] = label
                if code is not None:
                    codes.append(code)
                if label:
                    labels.append(label)
            record["series_key"] = ".".join(codes)
            record["name"] = " — ".join(labels)
            rows.append(record)
    return rows


def parse_sdmx_json(message: dict) -> list[dict]:
    """Flatten an ECB SDMX-JSON ``data`` message into observation records.

    Each record carries every series dimension (``<DIM>`` = code,
    ``<DIM>__label`` = name), the dot-joined ``series_key``, decoded
    series/observation attributes (by id), ``period`` (raw TIME_PERIOD),
    ``date`` (period-start ISO), and ``OBS_VALUE``.
    """
    datasets = message.get("dataSets") or []
    if not datasets:
        return []
    structure = message.get("structure", {})
    dims = structure.get("dimensions", {})
    series_dims = dims.get("series", [])
    obs_dims = dims.get("observation", []) or [{"id": "TIME_PERIOD", "values": []}]
    attrs = structure.get("attributes", {})
    series_attrs = attrs.get("series", [])
    obs_attrs = attrs.get("observation", [])
    time_values = obs_dims[0].get("values", [])

    def _decode(values: list, idx) -> tuple:
        if not isinstance(idx, int) or idx < 0 or idx >= len(values):
            return None, None
        item = values[idx]
        if isinstance(item, dict):
            return item.get("id"), item.get("name")
        return item, None

    rows: list[dict] = []
    for dataset in datasets:
        for series_key, series in dataset.get("series", {}).items():
            base: dict = {}
            key_codes: list[str] = []
            dim_ids: list[str] = []
            for pos, raw_idx in enumerate(series_key.split(":") if series_key else []):
                if pos >= len(series_dims):
                    break
                dim = series_dims[pos]
                code, label = _decode(dim.get("values", []), int(raw_idx))
                base[dim.get("id")] = code
                base[f"{dim.get('id')}__label"] = label
                dim_ids.append(dim.get("id"))
                if code is not None:
                    key_codes.append(code)
            base["series_key"] = ".".join(key_codes)
            base["_dim_ids"] = dim_ids

            for a_pos, a_idx in enumerate(series.get("attributes", []) or []):
                if a_idx is None or a_pos >= len(series_attrs):
                    continue
                attr = series_attrs[a_pos]
                code, label = _decode(attr.get("values", []), a_idx)
                if code is not None:
                    base[attr.get("id")] = code
                    base[f"{attr.get('id')}__label"] = label

            for obs_key, obs in series.get("observations", {}).items():
                row = dict(base)
                tv = (
                    time_values[int(obs_key)] if int(obs_key) < len(time_values) else {}
                )
                if not isinstance(tv, dict):
                    tv = {}
                row["period"] = tv.get("id")
                row["date"] = parse_sdmx_period(tv.get("id", ""), tv.get("start"))
                row["OBS_VALUE"] = obs[0] if obs else None
                for o_pos, o_attr in enumerate(obs_attrs):
                    val_pos = o_pos + 1
                    if val_pos < len(obs) and obs[val_pos] is not None:
                        code, label = _decode(o_attr.get("values", []), obs[val_pos])
                        if code is not None:
                            row[o_attr.get("id")] = code
                rows.append(row)
    return rows
