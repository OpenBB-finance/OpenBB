"""AgGrid Server-Side Row Model (SSRM) request/response shapes.

Routes whose POST body is (or subclasses) ``AgGridRowsRequest`` and/or
whose 200 response is ``AgGridRowsResponse`` get auto-promoted to widget
``type: "ssrm_table"`` by the platform_api widgets.json generator. The
type signature is the opt-in — authors don't need to set
``widget_config={"type": "ssrm_table"}`` on the route.

The field names mirror what AgGrid's server-side datasource sends and
expects, so they are camelCase by design and must not be renamed.
"""

from __future__ import annotations

from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

Row = TypeVar("Row")

SortDirection = Literal["asc", "desc"]
FilterType = Literal["text", "number", "date", "set", "boolean"]


class AgSortColumn(BaseModel):
    """One entry in AgGrid's ``sortModel``.

    AgGrid emits ``[{"colId": "<field>", "sort": "asc"|"desc"}]`` for
    every active sort. Order matters — the first entry is the primary
    sort key.
    """

    model_config = ConfigDict(extra="forbid")

    colId: str
    sort: SortDirection


class AgFilterModel(BaseModel):
    """One entry in AgGrid's ``filterModel`` keyed by colId.

    AgGrid's filter payload varies by column type (text/number/date/set
    each have their own operator vocabulary), so ``extra="allow"`` keeps
    the door open for the fields ag-grid adds for advanced operators
    (``filterTo``, ``dateFrom``, ``dateTo``, ``conditions``, ...).
    """

    model_config = ConfigDict(extra="allow")

    filterType: FilterType | None = None
    type: str | None = None
    filter: Any = None
    filterTo: Any = None
    values: list[Any] | None = None


class AgGroupingModel(BaseModel):
    """Row-grouping descriptor for SSRM.

    Sent when the user drags a column into the row-group panel. The
    backend only sees this when SSRM grouping is enabled on the widget.
    """

    model_config = ConfigDict(extra="forbid")

    rowGroupCols: list[dict[str, Any]] = Field(default_factory=list)
    valueCols: list[dict[str, Any]] = Field(default_factory=list)
    pivotCols: list[dict[str, Any]] = Field(default_factory=list)
    pivotMode: bool = False
    groupKeys: list[str] = Field(default_factory=list)


class AgGridRowsRequest(BaseModel):
    """Request body sent by an AgGrid SSRM datasource.

    Subclass this on a route to add provider-specific filters/params;
    the widget generator detects the SSRM contract by walking up the
    schema's ``allOf`` chain, so subclasses are recognized just like
    direct uses.
    """

    model_config = ConfigDict(extra="allow")

    startRow: int = Field(ge=0)
    endRow: int = Field(ge=0)
    sortModel: list[AgSortColumn] = Field(default_factory=list)
    filterModel: dict[str, AgFilterModel] = Field(default_factory=dict)
    grouping: AgGroupingModel | None = None


class AgGridRowsResponse(BaseModel, Generic[Row]):
    """Response body the SSRM datasource expects from the backend.

    ``rowData`` carries the page; ``rowCount`` is the *total* number of
    rows the datasource should report to AgGrid. ``rowCount`` lets the
    grid render the scroll thumb correctly even before all pages have
    loaded — set it to ``len(rowData)`` only when this is the last
    page.
    """

    model_config = ConfigDict(extra="forbid")

    rowData: list[Row]
    rowCount: int = Field(ge=0)
