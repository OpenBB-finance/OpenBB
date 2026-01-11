"""Pydantic models for PyWry toolbar components.

This module provides strongly-typed models for toolbar configurations:
- Individual input types (Button, Select, TextInput, etc.)
- Toolbar container with positioning
- Automatic component_id generation for state tracking

Usage:
    from pywry.toolbar import Toolbar, Button, Select, Option

    toolbar = Toolbar(
        position="top",
        items=[
            Button(label="Refresh", event="refresh", data={"force": True}),
            Select(
                label="View:",
                event="view_change",
                options=[Option(label="Table", value="table"), Option(label="Chart", value="chart")],
                selected="table",
            ),
        ],
    )

    # Use in show_dataframe
    show_dataframe(df, toolbars=[toolbar])
"""

from __future__ import annotations

import html
import json
import re
import uuid

from typing import TYPE_CHECKING, Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


if TYPE_CHECKING:
    from collections.abc import Sequence


# =============================================================================
# Type Aliases
# =============================================================================

ToolbarPosition = Literal["top", "bottom", "left", "right", "inside"]
ItemType = Literal["button", "select", "multiselect", "text", "number", "date", "range"]


# =============================================================================
# Event Validation
# =============================================================================

# Event pattern: namespace:event-name (e.g., "app:refresh", "view:change")
# Namespace: starts with letter, alphanumeric only
# Event name: starts with letter, alphanumeric + underscores + hyphens
EVENT_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9]*:[a-zA-Z][a-zA-Z0-9_-]*$")

# Reserved namespaces that users should not use
RESERVED_NAMESPACES = frozenset({"pywry", "plotly", "grid"})


def validate_event_format(event: str) -> bool:
    """Check if event matches namespace:event-name pattern.

    Parameters
    ----------
    event : str
        The event string to validate.

    Returns
    -------
    bool
        True if valid format, False otherwise.
    """
    return bool(EVENT_PATTERN.match(event))


# =============================================================================
# Helper Functions
# =============================================================================


def _generate_component_id(prefix: str = "pywry") -> str:
    """Generate a unique component ID for state tracking."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# =============================================================================
# Option Model (for Select/MultiSelect)
# =============================================================================


class Option(BaseModel):
    """A single option for select/multiselect inputs."""

    model_config = ConfigDict(frozen=True)

    label: str
    value: str | None = None

    @model_validator(mode="after")
    def set_value_from_label(self) -> Option:
        """If value is not provided, use label as value."""
        if self.value is None:
            # Can't modify frozen model, so we use object.__setattr__
            object.__setattr__(self, "value", self.label)
        return self


# =============================================================================
# Base ToolbarItem
# =============================================================================


class ToolbarItem(BaseModel):
    """Base class for all toolbar items.

    All items have:
    - component_id: Unique identifier for state tracking (auto-generated if not provided)
    - label: Display label (meaning varies by item type)
    - description: Tooltip/hover text for accessibility and user guidance
    - event: Event name emitted on interaction (format: namespace:event-name)
    - style: Optional inline CSS
    - disabled: Whether the item is disabled
    """

    model_config = ConfigDict(
        extra="forbid",  # Catch typos in field names
        validate_assignment=True,
    )

    component_id: str = Field(default_factory=lambda: _generate_component_id("item"))
    label: str = ""
    description: str = Field(default="", description="Tooltip text shown on hover")
    event: str = Field(
        default="toolbar:input",
        description="Event name in namespace:event-name format (e.g., 'view:change')",
    )
    style: str = ""
    disabled: bool = False

    @field_validator("event")
    @classmethod
    def validate_event_name(cls, v: str) -> str:
        """Validate event follows namespace:event-name pattern."""
        if not v or not v.strip():
            raise ValueError("Event name cannot be empty")
        v = v.strip()
        if not validate_event_format(v):
            raise ValueError(
                f"Invalid event format: '{v}'. "
                f"Must match 'namespace:event-name' pattern (e.g., 'toolbar:refresh', 'view:change'). "
                f"Namespace and event name must start with a letter and contain only alphanumeric characters, "
                f"underscores, or hyphens."
            )
        # Check for reserved namespaces
        namespace = v.split(":")[0].lower()
        if namespace in RESERVED_NAMESPACES:
            raise ValueError(
                f"Reserved namespace '{namespace}' cannot be used. "
                f"Reserved namespaces: {', '.join(sorted(RESERVED_NAMESPACES))}"
            )
        return v

    def _build_title_attr(self) -> str:
        """Build title attribute for tooltip if description is set."""
        if self.description:
            return f' title="{html.escape(self.description)}"'
        return ""

    def build_html(self) -> str:
        """Build HTML for this toolbar item. Override in subclasses."""
        raise NotImplementedError


# =============================================================================
# Button
# =============================================================================


class Button(ToolbarItem):
    """A clickable button that emits an event with optional data payload.

    Example:
        Button(label="Export", event="export:csv", data={"format": "csv"})
    """

    type: Literal["button"] = "button"
    data: dict[str, Any] = Field(default_factory=dict)

    def build_html(self) -> str:
        """Build button HTML."""
        data_json = json.dumps(self.data).replace('"', "&quot;")
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        onclick = (
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', JSON.parse(this.dataset.eventData || '{{}}')); "
            f"}} else {{ console.warn('PyWry not ready'); }}"
        )
        return (
            f'<button class="pywry-btn" id="{self.component_id}" '
            f'onclick="{onclick}" data-event-data="{data_json}" '
            f'style="{self.style}"{title_attr}{disabled_attr}>'
            f"{html.escape(self.label or 'Button')}</button>"
        )


# =============================================================================
# Select (Single-Select Dropdown)
# =============================================================================


class Select(ToolbarItem):
    """A single-select dropdown.

    Emits: {value: <selected_value>}

    Example:
        Select(
            label="Theme:",
            event="theme:change",
            options=[Option(label="Dark", value="dark"), Option(label="Light", value="light")],
            selected="dark",
        )
    """

    type: Literal["select"] = "select"
    options: list[Option] = Field(default_factory=list)
    selected: str = ""

    @field_validator("options", mode="before")
    @classmethod
    def normalize_options(cls, v: Any) -> list[Option]:
        """Accept list of dicts or Option objects."""
        if not v:
            return []
        result = []
        for opt in v:
            if isinstance(opt, Option):
                result.append(opt)
            elif isinstance(opt, dict):
                result.append(Option(**opt))
            elif isinstance(opt, str):
                result.append(Option(label=opt, value=opt))
            else:
                raise TypeError(f"Invalid option type: {type(opt)}")
        return result

    def build_html(self) -> str:
        """Build select HTML."""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        onchange = (
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', {{value: this.value}}); "
            f"}} else {{ console.warn('PyWry not ready'); }}"
        )
        options_html = "".join(
            f'<option value="{html.escape(str(opt.value))}"'
            f"{' selected' if str(opt.value) == self.selected else ''}>"
            f"{html.escape(str(opt.label))}</option>"
            for opt in self.options
        )

        select_html = (
            f'<select class="pywry-select" id="{self.component_id}" '
            f'onchange="{onchange}"{title_attr}{disabled_attr}>{options_html}</select>'
        )

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>'
                f"{select_html}</span>"
            )
        return f'<span style="{self.style}">{select_html}</span>' if self.style else select_html


# =============================================================================
# MultiSelect (Checkbox Group)
# =============================================================================


class MultiSelect(ToolbarItem):
    """A multi-select checkbox group.

    Emits: {values: [<selected_values>]}

    Example:
        MultiSelect(
            label="Columns:",
            event="columns:filter",
            options=[Option(label="Name"), Option(label="Age"), Option(label="City")],
            selected=["Name", "Age"],
        )
    """

    type: Literal["multiselect"] = "multiselect"
    options: list[Option] = Field(default_factory=list)
    selected: list[str] = Field(default_factory=list)

    @field_validator("options", mode="before")
    @classmethod
    def normalize_options(cls, v: Any) -> list[Option]:
        """Accept list of dicts or Option objects."""
        if not v:
            return []
        result = []
        for opt in v:
            if isinstance(opt, Option):
                result.append(opt)
            elif isinstance(opt, dict):
                result.append(Option(**opt))
            elif isinstance(opt, str):
                result.append(Option(label=opt, value=opt))
            else:
                raise TypeError(f"Invalid option type: {type(opt)}")
        return result

    @field_validator("selected", mode="before")
    @classmethod
    def normalize_selected(cls, v: Any) -> list[str]:
        """Convert single string to list."""
        if isinstance(v, str):
            return [v] if v else []
        return list(v) if v else []

    def build_html(self) -> str:
        """Build multiselect HTML."""
        selected_set = set(self.selected)
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()

        checkboxes = []
        for opt in self.options:
            val = html.escape(str(opt.value))
            lbl = html.escape(str(opt.label))
            checked = " checked" if str(opt.value) in selected_set else ""
            onchange = (
                f"(function(el) {{ "
                f"var container = el.closest('.pywry-multiselect'); "
                f"var checked = Array.from(container.querySelectorAll('input:checked')).map(i => i.value); "
                f"if (window.pywry && window.pywry.emit) {{ "
                f"window.pywry.emit('{self.event}', {{values: checked}}); "
                f"}} }})(this)"
            )
            checkboxes.append(
                f'<label class="pywry-checkbox-label">'
                f'<input type="checkbox" class="pywry-checkbox" value="{val}" '
                f'onchange="{onchange}"{checked}{disabled_attr}>{lbl}</label>'
            )

        checkboxes_html = "".join(checkboxes)
        inner = f'<div class="pywry-multiselect" id="{self.component_id}"{title_attr}>{checkboxes_html}</div>'

        if self.label:
            return (
                f'<span class="pywry-input-group" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{inner}</span>'
            )
        return inner


# =============================================================================
# TextInput
# =============================================================================


class TextInput(ToolbarItem):
    """A text input field with debounced change events.

    Emits: {value: <text_value>}

    Example:
        TextInput(label="Search:", event="search:query", placeholder="Type to search...", debounce=300)
    """

    type: Literal["text"] = "text"
    value: str = ""
    placeholder: str = ""
    debounce: int = Field(default=300, ge=0)

    def build_html(self) -> str:
        """Build text input HTML."""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        oninput = (
            f"clearTimeout(this._debounce); "
            f"this._debounce = setTimeout(() => {{ "
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', {{value: this.value}}); "
            f"}} }}, {self.debounce});"
        )
        input_html = (
            f'<input type="text" class="pywry-input pywry-input-text" '
            f'id="{self.component_id}" value="{html.escape(self.value)}" '
            f'placeholder="{html.escape(self.placeholder)}" oninput="{oninput}"{title_attr}{disabled_attr}>'
        )

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{input_html}</span>'
            )
        return input_html


# =============================================================================
# NumberInput
# =============================================================================


class NumberInput(ToolbarItem):
    """A numeric input field with optional min/max/step constraints.

    Emits: {value: <number_value>}

    Example:
        NumberInput(label="Limit:", event="limit:set", value=10, min=1, max=100, step=1)
    """

    type: Literal["number"] = "number"
    value: float | int | None = None
    min: float | int | None = None
    max: float | int | None = None
    step: float | int | None = None

    def build_html(self) -> str:
        """Build number input HTML."""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        onchange = (
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', {{value: parseFloat(this.value) || 0}}); "
            f"}} else {{ console.warn('PyWry not ready'); }}"
        )

        attrs = [f'id="{self.component_id}"']
        if self.value is not None:
            attrs.append(f'value="{self.value}"')
        if self.min is not None:
            attrs.append(f'min="{self.min}"')
        if self.max is not None:
            attrs.append(f'max="{self.max}"')
        if self.step is not None:
            attrs.append(f'step="{self.step}"')

        input_html = (
            f'<input type="number" class="pywry-input pywry-input-number" '
            f'{" ".join(attrs)} onchange="{onchange}"{title_attr}{disabled_attr}>'
        )

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{input_html}</span>'
            )
        return input_html


# =============================================================================
# DateInput
# =============================================================================


class DateInput(ToolbarItem):
    """A date picker input.

    Emits: {value: <date_string>} (YYYY-MM-DD format)

    Example:
        DateInput(label="Start Date:", event="date:start", value="2025-01-01", min="2020-01-01")
    """

    type: Literal["date"] = "date"
    value: str = ""
    min: str = ""
    max: str = ""

    def build_html(self) -> str:
        """Build date input HTML."""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        onchange = (
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', {{value: this.value}}); "
            f"}} else {{ console.warn('PyWry not ready'); }}"
        )

        attrs = [f'id="{self.component_id}"']
        if self.value:
            attrs.append(f'value="{html.escape(self.value)}"')
        if self.min:
            attrs.append(f'min="{html.escape(self.min)}"')
        if self.max:
            attrs.append(f'max="{html.escape(self.max)}"')

        input_html = (
            f'<input type="date" class="pywry-input pywry-input-date" '
            f'{" ".join(attrs)} onchange="{onchange}"{title_attr}{disabled_attr}>'
        )

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{input_html}</span>'
            )
        return input_html


# =============================================================================
# RangeInput (Slider)
# =============================================================================


class RangeInput(ToolbarItem):
    """A range slider input.

    Emits: {value: <number_value>}

    Example:
        RangeInput(label="Zoom:", event="zoom:level", value=50, min=0, max=100, step=5, show_value=True)
    """

    type: Literal["range"] = "range"
    value: float | int = 50
    min: float | int = 0
    max: float | int = 100
    step: float | int = 1
    show_value: bool = True

    def build_html(self) -> str:
        """Build range input HTML."""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        onchange = (
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', {{value: parseFloat(this.value)}}); "
            f"}} "
            f"var display = this.nextElementSibling; "
            f"if (display) display.textContent = this.value;"
        )

        range_html = (
            f'<input type="range" class="pywry-input pywry-input-range" '
            f'id="{self.component_id}" value="{self.value}" min="{self.min}" '
            f'max="{self.max}" step="{self.step}" oninput="{onchange}"{title_attr}{disabled_attr}>'
        )

        if self.show_value:
            range_html += f'<span class="pywry-range-value">{self.value}</span>'

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{range_html}</span>'
            )
        return range_html


# =============================================================================
# Union Type for All Toolbar Items
# =============================================================================

AnyToolbarItem = Annotated[
    Button | Select | MultiSelect | TextInput | NumberInput | DateInput | RangeInput,
    Field(discriminator="type"),
]


# =============================================================================
# Toolbar Container
# =============================================================================


class Toolbar(BaseModel):
    """A toolbar container with positioned items.

    Attributes
    ----------
        component_id: Unique identifier for this toolbar (auto-generated if not provided)
        position: Where to place the toolbar ("top", "bottom", "left", "right", "inside")
        items: List of toolbar items (Button, Select, TextInput, etc.)
        style: Optional inline CSS for the toolbar container

    Example:
        Toolbar(
            position="top",
            items=[
                Button(label="Refresh", event="refresh"),
                Select(label="View:", event="view:change", options=[...]),
            ],
        )
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    component_id: str = Field(default_factory=lambda: _generate_component_id("toolbar"))
    position: ToolbarPosition = "top"
    items: list[AnyToolbarItem] = Field(default_factory=list)
    style: str = ""

    @field_validator("items", mode="before")
    @classmethod
    def normalize_items(cls, v: Any) -> list[ToolbarItem]:
        """Accept list of dicts or ToolbarItem objects."""
        if not v:
            return []
        result: list[ToolbarItem] = []
        for item in v:
            if isinstance(item, ToolbarItem):
                result.append(item)
            elif isinstance(item, dict):
                item_type = item.get("type", "button")
                item_class = _ITEM_TYPE_MAP.get(item_type)
                if item_class is None:
                    raise ValueError(f"Unknown toolbar item type: {item_type}")
                result.append(item_class(**item))
            else:
                raise TypeError(f"Invalid toolbar item type: {type(item)}")
        return result

    def build_html(self) -> str:
        """Build complete toolbar HTML."""
        if not self.items:
            return ""

        item_htmls = [item.build_html() for item in self.items]
        container_class = f"pywry-toolbar pywry-toolbar-{self.position}"
        style_attr = f' style="{self.style}"' if self.style else ""

        return (
            f'<div class="{container_class}" id="{self.component_id}"{style_attr}>'
            f"{''.join(item_htmls)}</div>"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for backward compatibility with dict-based API."""
        return {
            "component_id": self.component_id,
            "position": self.position,
            "items": [
                {
                    "component_id": item.component_id,
                    "type": item.type,
                    "label": item.label,
                    "event": item.event,
                    "style": item.style,
                    "disabled": item.disabled,
                    **item.model_dump(
                        exclude={"component_id", "type", "label", "event", "style", "disabled"}
                    ),
                }
                for item in self.items
            ],
            "style": self.style,
        }


# =============================================================================
# Item Type Mapping
# =============================================================================

_ITEM_TYPE_MAP: dict[str, type[ToolbarItem]] = {
    "button": Button,
    "select": Select,
    "multiselect": MultiSelect,
    "text": TextInput,
    "number": NumberInput,
    "date": DateInput,
    "range": RangeInput,
}


# =============================================================================
# Helper Functions for Building Toolbars
# =============================================================================


def build_toolbar_html(toolbar: Toolbar | dict[str, Any]) -> str:
    """Build HTML for a single toolbar.

    Parameters
    ----------
    toolbar : Toolbar or dict
        Toolbar configuration (Toolbar model or legacy dict format).

    Returns
    -------
    str
        HTML string for the toolbar.
    """
    if isinstance(toolbar, dict):
        toolbar = Toolbar(**toolbar)
    return toolbar.build_html()


def build_toolbars_html(toolbars: Sequence[Toolbar | dict[str, Any]] | None) -> str:
    """Build HTML for multiple toolbars.

    Parameters
    ----------
    toolbars : list of Toolbar or dict, or None
        List of toolbar configurations.

    Returns
    -------
    str
        Combined HTML string for all toolbars.
    """
    if not toolbars:
        return ""

    html_parts = []
    for toolbar in toolbars:
        toolbar_html = build_toolbar_html(toolbar)
        if toolbar_html:
            html_parts.append(toolbar_html)

    return "".join(html_parts)


def build_toolbars_by_position(
    toolbars: Sequence[Toolbar | dict[str, Any]] | None,
) -> dict[str, str]:
    """Build toolbars grouped by position.

    Parameters
    ----------
    toolbars : list of Toolbar or dict, or None
        List of toolbar configurations.

    Returns
    -------
    dict
        Mapping of position -> combined HTML for toolbars at that position.
        Keys: "top", "bottom", "left", "right", "inside"
    """
    result: dict[str, list[str]] = {
        "top": [],
        "bottom": [],
        "left": [],
        "right": [],
        "inside": [],
    }

    if not toolbars:
        return dict.fromkeys(result, "")

    for tb in toolbars:
        tb_model = Toolbar(**tb) if isinstance(tb, dict) else tb
        toolbar_html = tb_model.build_html()
        if toolbar_html:
            result[tb_model.position].append(toolbar_html)

    return {k: "".join(v) for k, v in result.items()}
