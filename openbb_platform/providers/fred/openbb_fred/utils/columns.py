"""Declared value columns for the models whose series are known ahead of time."""

import re
from typing import Any

from pydantic import Field

TIME_COLUMN: dict[str, Any] = {"x-widget_config": {"chartDataType": "time"}}

_SEPARATORS = re.compile(r"[^0-9a-zA-Z]+")


def column_name(label: str) -> str:
    """Return the field name one published series is carried under.

    Parameters
    ----------
    label : str
        The label the series is known by, such as 'year15+' or '1.5y'.

    Returns
    -------
    str
        A valid field name, lowercased, with every separator folded to an
        underscore and a leading digit prefixed so the name stays an
        identifier.
    """
    slug = _SEPARATORS.sub("_", label.strip().lower().replace("+", "_plus")).strip("_")

    return f"year_{slug}" if slug[:1].isdigit() else slug


def series_field(label: str, unit: str | None = "percent") -> tuple:
    """Declare one value column of a wide model.

    Parameters
    ----------
    label : str
        The header the column carries in the table and the chart legend.
    unit : str or None
        The unit the values are published in, or None where one column serves
        more than one unit.

    Returns
    -------
    tuple
        The annotation and field, ready for ``pydantic.create_model``.
    """
    config: dict[str, Any] = {
        "headerName": label,
        "cellDataType": "number",
        "chartDataType": "series",
    }
    extra: dict[str, Any] = {"x-widget_config": config}

    if unit is not None:
        extra["x-unit_measurement"] = unit

    return (
        float | None,
        Field(default=None, description=f"{label}.", json_schema_extra=extra),
    )
