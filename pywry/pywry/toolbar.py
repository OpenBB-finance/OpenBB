# pylint: disable=too-many-lines
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

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


if TYPE_CHECKING:
    from collections.abc import Sequence


# Directory containing frontend source files
_SRC_DIR = Path(__file__).parent / "frontend" / "src"


# =============================================================================
# Type Aliases
# =============================================================================

ToolbarPosition = Literal["header", "footer", "top", "bottom", "left", "right", "inside"]
ItemType = Literal[
    "button",
    "select",
    "multiselect",
    "text",
    "number",
    "date",
    "slider",
    "range",
    "toggle",
    "checkbox",
    "radio",
    "div",
]


# =============================================================================
# Event Validation
# =============================================================================

# Event pattern: namespace:event-name (e.g., "app:refresh", "view:change")
# Namespace: starts with letter, alphanumeric only
# Event name: starts with letter, alphanumeric + underscores + hyphens
EVENT_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9]*:[a-zA-Z][a-zA-Z0-9_-]*$")

# Reserved namespaces that users should not use
RESERVED_NAMESPACES = frozenset({"pywry", "plotly", "grid"})

# Exceptions to reserved namespaces
ALLOWED_RESERVED_PATTERNS = [
    "plotly:modebar_",
]


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


def _generate_component_id(component_type: str = "item") -> str:
    """Generate a unique component ID for state tracking.

    Parameters
    ----------
    component_type : str
        The type of component (e.g., "button", "select", "toolbar").

    Returns
    -------
    str
        A unique ID in the format "{component_type}-{uuid[:8]}".
    """
    return f"{component_type}-{uuid.uuid4().hex[:8]}"


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

    component_id: str = Field(default="")
    label: str = ""
    description: str = Field(default="", description="Tooltip text shown on hover")
    event: str = Field(
        default="toolbar:input",
        description="Event name in namespace:event-name format (e.g., 'view:change')",
    )
    style: str = ""
    disabled: bool = False

    @model_validator(mode="after")
    def auto_generate_component_id(self) -> ToolbarItem:
        """Auto-generate component_id based on type if not provided."""
        if not self.component_id:
            # Get the type from the subclass (e.g., "button", "select", "div")
            component_type = getattr(self, "type", "item")
            object.__setattr__(self, "component_id", _generate_component_id(component_type))
        return self

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
            # Check exceptions
            is_allowed = False
            for pattern in ALLOWED_RESERVED_PATTERNS:
                if v.startswith(pattern):
                    is_allowed = True
                    break

            if not is_allowed:
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

    Parameters
    ----------
        variant: Button style variant:
            - "primary" (theme-aware: light bg in dark mode, accent in light mode)
            - "secondary" (subtle background, theme-aware)
            - "neutral" (always blue accent - use for primary actions)
            - "ghost" (transparent)
            - "outline" (bordered)
            - "danger" (red)
            - "warning" (orange)
            - "icon" (ghost style, square aspect ratio for icon-only buttons)
        size: Button size variant:
            - None (default size)
            - "xs" (extra small)
            - "sm" (small)
            - "lg" (large)
            - "xl" (extra large)

    Example:
        Button(label="Export", event="export:csv", data={"format": "csv"})
        Button(label="Cancel", event="cancel", variant="secondary")
        Button(label="⚙", event="settings", variant="icon")
        Button(label="Submit", event="submit", variant="neutral", size="lg")
    """

    type: Literal["button"] = "button"
    data: dict[str, Any] = Field(default_factory=dict)
    variant: Literal[
        "primary", "secondary", "neutral", "ghost", "outline", "danger", "warning", "icon"
    ] = "primary"
    size: Literal["xs", "sm", "lg", "xl"] | None = None

    def build_html(self) -> str:
        """Build button HTML."""
        variant_class = f" pywry-btn-{self.variant}" if self.variant != "primary" else ""
        size_class = f" pywry-btn-{self.size}" if self.size else ""
        disabled_class = " pywry-disabled" if self.disabled else ""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        style_attr = f' style="{self.style}"' if self.style else ""

        # Data payload as JSON attribute
        data_attr = ""
        if self.data:
            data_json = html.escape(json.dumps(self.data), quote=True)
            data_attr = f' data-data="{data_json}"'

        return (
            f'<button class="pywry-btn pywry-toolbar-button{variant_class}{size_class}{disabled_class}" '
            f'id="{self.component_id}" data-event="{self.event}"{data_attr}'
            f"{style_attr}{title_attr}{disabled_attr}>"
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
        """Build custom dropdown HTML (not native select, for consistent styling)."""
        disabled_attr = " pywry-disabled" if self.disabled else ""
        title_attr = self._build_title_attr()

        # Find selected option label
        selected_label = self.selected
        for opt in self.options:
            if str(opt.value) == self.selected:
                selected_label = opt.label
                break

        # Build options HTML
        options_html = "".join(
            f'<div class="pywry-dropdown-option{" pywry-selected" if str(opt.value) == self.selected else ""}" '
            f'data-value="{html.escape(str(opt.value))}">'
            f"{html.escape(str(opt.label))}</div>"
            for opt in self.options
        )

        # Custom dropdown structure
        dropdown_html = (
            f'<div class="pywry-dropdown{disabled_attr}" id="{self.component_id}" '
            f'data-event="{self.event}"{title_attr}>'
            f'<div class="pywry-dropdown-selected">'
            f'<span class="pywry-dropdown-text">{html.escape(str(selected_label))}</span>'
            f'<span class="pywry-dropdown-arrow"></span>'
            f"</div>"
            f'<div class="pywry-dropdown-menu">{options_html}</div>'
            f"</div>"
        )

        if self.label:
            return (
                f'<div class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>'
                f"{dropdown_html}</div>"
            )
        return f'<div style="{self.style}">{dropdown_html}</div>' if self.style else dropdown_html


# =============================================================================
# MultiSelect (Checkbox Group)
# =============================================================================


class MultiSelect(ToolbarItem):
    """A multi-select dropdown with checkboxes.

    Emits: {values: [<selected_values>]}

    Selected items appear at the top of the dropdown, unselected items below.

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
        """Build multiselect dropdown HTML with checkboxes."""
        selected_set = set(self.selected)
        disabled_attr = " pywry-disabled" if self.disabled else ""
        title_attr = self._build_title_attr()

        # Build display text for selected items
        selected_labels = [opt.label for opt in self.options if str(opt.value) in selected_set]

        if len(selected_labels) == 0:
            display_text = "Select..."
        elif len(selected_labels) <= 2:
            display_text = ", ".join(selected_labels)
        else:
            display_text = f"{len(selected_labels)} selected"

        # Separate options: selected first, then unselected
        selected_opts = [opt for opt in self.options if str(opt.value) in selected_set]
        unselected_opts = [opt for opt in self.options if str(opt.value) not in selected_set]
        sorted_options = selected_opts + unselected_opts

        # Build options HTML with checkboxes
        options_html_parts = []
        for opt in sorted_options:
            val = html.escape(str(opt.value))
            lbl = html.escape(str(opt.label))
            checked = " checked" if str(opt.value) in selected_set else ""
            selected_class = " pywry-selected" if str(opt.value) in selected_set else ""
            options_html_parts.append(
                f'<label class="pywry-multiselect-option{selected_class}" data-value="{val}">'
                f'<input type="checkbox" class="pywry-multiselect-checkbox" value="{val}"{checked}>'
                f'<span class="pywry-multiselect-label">{lbl}</span>'
                f"</label>"
            )
        options_html = "".join(options_html_parts)

        # Header with search and select all/none buttons
        header_html = (
            '<div class="pywry-multiselect-header">'
            '<input type="text" class="pywry-multiselect-search" placeholder="Search...">'
            '<div class="pywry-multiselect-actions">'
            '<button type="button" class="pywry-multiselect-action" data-action="all">All</button>'
            '<button type="button" class="pywry-multiselect-action" data-action="none">None</button>'
            "</div>"
            "</div>"
        )

        # Custom dropdown structure (similar to Select but with multiselect class)
        dropdown_html = (
            f'<div class="pywry-dropdown pywry-multiselect{disabled_attr}" id="{self.component_id}" '
            f'data-event="{self.event}"{title_attr}>'
            f'<div class="pywry-dropdown-selected">'
            f'<span class="pywry-dropdown-text">{html.escape(str(display_text))}</span>'
            f'<span class="pywry-dropdown-arrow"></span>'
            f"</div>"
            f'<div class="pywry-dropdown-menu pywry-multiselect-menu">'
            f"{header_html}"
            f'<div class="pywry-multiselect-options">{options_html}</div>'
            f"</div>"
            f"</div>"
        )

        if self.label:
            return (
                f'<div class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>'
                f"{dropdown_html}</div>"
            )
        return f'<div style="{self.style}">{dropdown_html}</div>' if self.style else dropdown_html


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
            f"var _el = this; "
            f"this._debounce = setTimeout(() => {{ "
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', {{value: _el.value, componentId: '{self.component_id}'}}, _el); "
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
        """Build number input HTML with custom spinner buttons."""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        onchange = (
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', {{value: parseFloat(this.value) || 0, componentId: '{self.component_id}'}}, this); "
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

        # Custom spinner buttons
        spinner_html = (
            '<span class="pywry-number-spinner">'
            '<button type="button" tabindex="-1" '
            "onclick=\"var inp=this.parentElement.previousElementSibling;inp.stepUp();inp.dispatchEvent(new Event('change'));\">&#9650;</button>"
            '<button type="button" tabindex="-1" '
            "onclick=\"var inp=this.parentElement.previousElementSibling;inp.stepDown();inp.dispatchEvent(new Event('change'));\">&#9660;</button>"
            "</span>"
        )

        # Wrap input and spinner together
        wrapper_html = f'<span class="pywry-number-wrapper">{input_html}{spinner_html}</span>'

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{wrapper_html}</span>'
            )
        return wrapper_html


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
            f"window.pywry.emit('{self.event}', {{value: this.value, componentId: '{self.component_id}'}}, this); "
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


class SliderInput(ToolbarItem):
    """A single-value slider input.

    Emits: {value: <number_value>}

    Example:
        SliderInput(label="Zoom:", event="zoom:level", value=50, min=0, max=100, step=5, show_value=True)
    """

    type: Literal["slider"] = "slider"
    value: float | int = 50
    min: float | int = 0
    max: float | int = 100
    step: float | int = 1
    show_value: bool = True
    debounce: int = 50

    def build_html(self) -> str:
        """Build range input HTML."""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        debounce_ms = self.debounce
        onchange = (
            f"(function(el) {{"
            f"var display = el.nextElementSibling; if (display) display.textContent = el.value;"
            f"clearTimeout(el._debounce);"
            f"el._debounce = setTimeout(function() {{"
            f"if (window.pywry && window.pywry.emit) {{"
            f"window.pywry.emit('{self.event}', {{value: parseFloat(el.value), componentId: '{self.component_id}'}}, el);"
            f"}}"
            f"}}, {debounce_ms});"
            f"}})(this)"
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
# RangeInput (Dual-Handle Range Selector)
# =============================================================================


class RangeInput(ToolbarItem):
    """A dual-handle range slider for selecting a value range.

    Emits: {start: <number>, end: <number>}

    This component provides a single slider track with two handles for selecting
    a minimum and maximum value. Unlike SliderInput which selects a single value,
    RangeInput allows users to define a range of values.

    Example:
        RangeInput(
            label="Price Range:",
            event="filter:price",
            start=100,
            end=500,
            min=0,
            max=1000,
            step=10,
        )
    """

    type: Literal["range"] = "range"
    start: float | int = 0
    end: float | int = 100
    min: float | int = 0
    max: float | int = 100
    step: float | int = 1
    show_value: bool = True
    debounce: int = 50

    def build_html(self) -> str:
        """Build dual-handle range slider HTML with overlaid inputs."""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        debounce_ms = self.debounce

        range_val = self.max - self.min
        start_pct = ((self.start - self.min) / range_val * 100) if range_val else 0
        end_pct = ((self.end - self.min) / range_val * 100) if range_val else 100

        emit_js = (
            f"(function(el) {{"
            f"var group = el.closest('.pywry-range-group');"
            f"if (!group) return;"
            f"var startEl = group.querySelector('input[data-range=start]');"
            f"var endEl = group.querySelector('input[data-range=end]');"
            f"var fill = group.querySelector('.pywry-range-track-fill');"
            f"var startDisp = group.querySelector('.pywry-range-start-value');"
            f"var endDisp = group.querySelector('.pywry-range-end-value');"
            f"if (!startEl || !endEl) return;"
            f"var startVal = parseFloat(startEl.value);"
            f"var endVal = parseFloat(endEl.value);"
            f"var minVal = parseFloat(startEl.min);"
            f"var maxVal = parseFloat(startEl.max);"
            f"if (startVal > endVal) {{"
            f"if (el.dataset.range === 'start') {{ startVal = endVal; startEl.value = endVal; }}"
            f"else {{ endVal = startVal; endEl.value = startVal; }}"
            f"}}"
            f"var range = maxVal - minVal;"
            f"var startPct = ((startVal - minVal) / range) * 100;"
            f"var endPct = ((endVal - minVal) / range) * 100;"
            f"if (fill) {{ fill.style.left = startPct + '%'; fill.style.width = (endPct - startPct) + '%'; }}"
            f"if (startDisp) startDisp.textContent = startVal;"
            f"if (endDisp) endDisp.textContent = endVal;"
            f"clearTimeout(group._debounce);"
            f"group._debounce = setTimeout(function() {{"
            f"if (window.pywry && window.pywry.emit) {{"
            f"window.pywry.emit('{self.event}', {{"
            f"start: startVal, end: endVal, componentId: '{self.component_id}'"
            f"}}, el);"
            f"}}"
            f"}}, {debounce_ms});"
            f"}})(this)"
        )

        start_value_html = (
            f'<span class="pywry-range-value pywry-range-start-value">{self.start}</span>'
            if self.show_value
            else ""
        )
        end_value_html = (
            f'<span class="pywry-range-value pywry-range-end-value">{self.end}</span>'
            if self.show_value
            else ""
        )

        track_html = (
            f'<div class="pywry-range-track">'
            f'<div class="pywry-range-track-bg"></div>'
            f'<div class="pywry-range-track-fill" style="left: {start_pct}%; width: {end_pct - start_pct}%;"></div>'
            f'<input type="range" data-range="start" value="{self.start}" min="{self.min}" '
            f'max="{self.max}" step="{self.step}" oninput="{emit_js}"{title_attr}{disabled_attr}>'
            f'<input type="range" data-range="end" value="{self.end}" min="{self.min}" '
            f'max="{self.max}" step="{self.step}" oninput="{emit_js}"{title_attr}{disabled_attr}>'
            f"</div>"
        )

        range_html = (
            f'<span class="pywry-range-group" id="{self.component_id}">'
            f"{start_value_html}"
            f"{track_html}"
            f"{end_value_html}"
            f"</span>"
        )

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{range_html}</span>'
            )
        return range_html


# =============================================================================
# Toggle (Boolean Switch)
# =============================================================================


class Toggle(ToolbarItem):
    """A toggle switch for boolean values.

    Emits: {value: <boolean>}

    Example:
        Toggle(label="Dark Mode:", event="theme:toggle", value=True)
    """

    type: Literal["toggle"] = "toggle"
    value: bool = False

    def build_html(self) -> str:
        """Build toggle switch HTML."""
        disabled_attr = " pywry-disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        checked_attr = " checked" if self.value else ""
        checked_class = " pywry-toggle-checked" if self.value else ""
        onchange = (
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', {{value: this.checked, componentId: '{self.component_id}'}}, this); "
            f"}} else {{ console.warn('PyWry not ready'); }}"
        )

        toggle_html = (
            f'<label class="pywry-toggle{checked_class}{disabled_attr}" id="{self.component_id}"{title_attr}>'
            f'<input type="checkbox" class="pywry-toggle-input" onchange="{onchange}"{checked_attr}>'
            f'<span class="pywry-toggle-slider"></span>'
            f"</label>"
        )

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{toggle_html}</span>'
            )
        return toggle_html


# =============================================================================
# Checkbox (Boolean Checkbox)
# =============================================================================


class Checkbox(ToolbarItem):
    """A single checkbox for boolean values.

    Emits: {value: <boolean>}

    Example:
        Checkbox(label="Enable notifications", event="settings:notify", value=True)
    """

    type: Literal["checkbox"] = "checkbox"
    value: bool = False

    def build_html(self) -> str:
        """Build checkbox HTML."""
        disabled_attr = " disabled" if self.disabled else ""
        disabled_class = " pywry-disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        checked_attr = " checked" if self.value else ""
        onchange = (
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', {{value: this.checked, componentId: '{self.component_id}'}}, this); "
            f"}} else {{ console.warn('PyWry not ready'); }}"
        )

        checkbox_html = (
            f'<label class="pywry-checkbox{disabled_class}" id="{self.component_id}"{title_attr}>'
            f'<input type="checkbox" class="pywry-checkbox-input" onchange="{onchange}"{checked_attr}{disabled_attr}>'
            f'<span class="pywry-checkbox-box"></span>'
            f'<span class="pywry-checkbox-label">{html.escape(self.label)}</span>'
            f"</label>"
        )

        if self.style:
            return f'<span style="{self.style}">{checkbox_html}</span>'
        return checkbox_html


# =============================================================================
# RadioGroup (Radio Buttons)
# =============================================================================


class RadioGroup(ToolbarItem):
    """A group of radio buttons for single selection.

    Emits: {value: <selected_value>}

    Parameters
    ----------
        direction: Layout direction - "horizontal" or "vertical"

    Example:
        RadioGroup(
            label="View:",
            event="view:change",
            options=[Option(label="List", value="list"), Option(label="Grid", value="grid")],
            selected="list",
            direction="horizontal",
        )
    """

    type: Literal["radio"] = "radio"
    options: list[Option] = Field(default_factory=list)
    selected: str = ""
    direction: Literal["horizontal", "vertical"] = "horizontal"

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
        """Build radio group HTML."""
        disabled_class = " pywry-disabled" if self.disabled else ""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        direction_class = f" pywry-radio-{self.direction}"

        onchange = (
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', {{value: this.value, componentId: '{self.component_id}'}}, this); "
            f"}} else {{ console.warn('PyWry not ready'); }}"
        )

        # Build radio options
        options_html_parts = []
        for opt in self.options:
            val = html.escape(str(opt.value))
            lbl = html.escape(str(opt.label))
            checked = " checked" if str(opt.value) == self.selected else ""
            options_html_parts.append(
                f'<label class="pywry-radio-option">'
                f'<input type="radio" name="{self.component_id}" value="{val}" '
                f'onchange="{onchange}"{checked}{disabled_attr}>'
                f'<span class="pywry-radio-button"></span>'
                f'<span class="pywry-radio-label">{lbl}</span>'
                f"</label>"
            )
        options_html = "".join(options_html_parts)

        radio_html = (
            f'<div class="pywry-radio-group{direction_class}{disabled_class}" '
            f'id="{self.component_id}" data-event="{self.event}"{title_attr}>'
            f"{options_html}"
            f"</div>"
        )

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{radio_html}</span>'
            )
        return f'<span style="{self.style}">{radio_html}</span>' if self.style else radio_html


# =============================================================================
# TabGroup (Tab-style Selection)
# =============================================================================


class TabGroup(ToolbarItem):
    """A group of tabs for single-value selection with tab-style appearance.

    Similar to RadioGroup but styled as tabs. Useful for view switching,
    mode selection, or any mutually exclusive option set that benefits
    from a tab-like visual appearance.

    Emits: {componentId, value: <selected_value>}

    Parameters
    ----------
        options: List of Option objects (label + value).
        selected: Currently selected value.
        size: Tab size - "sm", "md" (default), or "lg".

    Example:
        TabGroup(
            label="View:",
            event="view:change",
            options=[
                Option(label="Table", value="table"),
                Option(label="Chart", value="chart"),
                Option(label="Map", value="map"),
            ],
            selected="table",
        )
    """

    type: Literal["tab"] = "tab"
    options: list[Option] = Field(default_factory=list)
    selected: str = ""
    size: Literal["sm", "md", "lg"] = "md"

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
        """Build tab group HTML."""
        disabled_class = " pywry-disabled" if self.disabled else ""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()
        size_class = f" pywry-tab-{self.size}" if self.size != "md" else ""

        onclick = (
            f"if (window.pywry && window.pywry.emit) {{ "
            f"this.parentElement.querySelectorAll('.pywry-tab').forEach(t => t.classList.remove('pywry-tab-active')); "
            f"this.classList.add('pywry-tab-active'); "
            f"window.pywry.emit('{self.event}', {{value: this.dataset.value, componentId: '{self.component_id}'}}, this); "
            f"}} else {{ console.warn('PyWry not ready'); }}"
        )

        # Build tab buttons
        tabs_html_parts = []
        for opt in self.options:
            val = html.escape(str(opt.value))
            lbl = html.escape(str(opt.label))
            active_class = " pywry-tab-active" if str(opt.value) == self.selected else ""
            tabs_html_parts.append(
                f'<button type="button" class="pywry-tab{active_class}" '
                f'data-value="{val}" onclick="{onclick}"{disabled_attr}>{lbl}</button>'
            )
        tabs_html = "".join(tabs_html_parts)

        tab_group_html = (
            f'<div class="pywry-tab-group{size_class}{disabled_class}" '
            f'id="{self.component_id}" data-event="{self.event}"{title_attr}>'
            f"{tabs_html}"
            f"</div>"
        )

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{tab_group_html}</span>'
            )
        return (
            f'<span style="{self.style}">{tab_group_html}</span>' if self.style else tab_group_html
        )


# =============================================================================
# Div (Container for Custom HTML Content)
# =============================================================================


class Div(ToolbarItem):
    """A container div for custom HTML content within a toolbar.

    Supports nested toolbar items and custom scripts for advanced layouts.
    Parent context (component IDs) is passed to children via data-parent-id attribute.

    Emits: No automatic events (unless content has interactive elements)

    Parameters
    ----------
        content: HTML content to render inside the div.
        script: JS file path or inline string to inject (executed after toolbar script).
        class_name: Custom CSS class for the div container.
        children: Nested toolbar items (Button, Select, other Divs, etc.).

    Example:
        Div(
            content="<h3>Controls</h3>",
            class_name="my-controls",
            children=[
                Button(label="Action", event="app:action"),
                Div(content="<span>Nested</span>", class_name="nested-div"),
            ],
        )
    """

    type: Literal["div"] = "div"
    content: str = ""
    script: str | Path | None = Field(
        default=None,
        description="JS file path or inline script for this container",
    )
    class_name: str = Field(
        default="",
        description="Custom CSS class for the div (added to pywry-div)",
    )
    # Forward reference to AnyToolbarItem - will be resolved via model_rebuild()
    children: list[Any] | None = Field(
        default=None,
        description="Nested toolbar items (supports all item types including Div)",
    )

    def build_html(self, parent_id: str | None = None) -> str:
        """Build div HTML with content and nested children.

        Parameters
        ----------
        parent_id : str | None
            Parent component ID for context chain inheritance.

        Returns
        -------
        str
            HTML string for the div container.
        """
        classes = ["pywry-div"]
        if self.class_name:
            classes.append(self.class_name)

        attrs = [
            f'class="{" ".join(classes)}"',
            f'id="{self.component_id}"',
            f'data-component-id="{self.component_id}"',
        ]
        if parent_id:
            attrs.append(f'data-parent-id="{parent_id}"')
        if self.style:
            attrs.append(f'style="{self.style}"')

        # Build children HTML
        children_html = ""
        if self.children:
            for child in self.children:
                if hasattr(child, "build_html"):
                    # Pass this div's component_id as parent context
                    if isinstance(child, Div):
                        children_html += child.build_html(parent_id=self.component_id)
                    else:
                        children_html += child.build_html()

        return f"<div {' '.join(attrs)}>{self.content}{children_html}</div>"

    def collect_scripts(self) -> list[str]:
        """Collect scripts from this div and all nested children (depth-first).

        Returns
        -------
        list[str]
            List of script content strings (file contents or inline scripts).
        """
        scripts: list[str] = []

        # This div's script first (parent before children)
        if self.script:
            if isinstance(self.script, Path) or (
                isinstance(self.script, str)
                and not self.script.strip().startswith(
                    (
                        "(",
                        "{",
                        "function",
                        "//",
                        "/*",
                        "var ",
                        "let ",
                        "const ",
                        "if ",
                        "for ",
                        "while ",
                    )
                )
            ):
                # Might be a file path - try to read it
                script_path = Path(self.script) if isinstance(self.script, str) else self.script
                if script_path.exists():
                    scripts.append(script_path.read_text(encoding="utf-8"))
                else:
                    # Treat as inline script
                    scripts.append(str(self.script))
            else:
                scripts.append(str(self.script))

        # Children's scripts (depth-first)
        if self.children:
            for child in self.children:
                if isinstance(child, Div):
                    scripts.extend(child.collect_scripts())

        return scripts


# =============================================================================
# Union Type for All Toolbar Items
# =============================================================================

AnyToolbarItem = Annotated[
    Button
    | Select
    | MultiSelect
    | TextInput
    | NumberInput
    | DateInput
    | SliderInput
    | RangeInput
    | Toggle
    | Checkbox
    | RadioGroup
    | TabGroup
    | Div,
    Field(discriminator="type"),
]


# Rebuild Div model to resolve forward reference for nested children
Div.model_rebuild()


# =============================================================================
# Toolbar Container
# =============================================================================


class Toolbar(BaseModel):
    """A toolbar container with positioned items.

    Attributes
    ----------
        component_id: Unique identifier for this toolbar (auto-generated if not provided)
        position: Where to place the toolbar ("top", "bottom", "left", "right", "inside")
        items: List of toolbar items (Button, Select, TextInput, Div, etc.)
        style: Optional inline CSS for the toolbar container
        script: JS file path or inline string to inject into the toolbar
        class_name: Custom CSS class added to the toolbar container
        collapsible: Enable collapse/expand behavior with toggle button
        resizable: Enable drag-to-resize on toolbar edge (direction based on position)

    Example:
        Toolbar(
            position="top",
            class_name="my-toolbar",
            collapsible=True,
            resizable=True,
            items=[
                Button(label="Refresh", event="refresh"),
                Select(label="View:", event="view:change", options=[...]),
                Div(content="<span>Custom</span>", class_name="custom-section"),
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

    # New optional parameters
    script: str | Path | None = Field(
        default=None,
        description="JS file path or inline script for the toolbar",
    )
    class_name: str = Field(
        default="",
        description="Custom CSS class added to the toolbar container",
    )
    collapsible: bool = Field(
        default=False,
        description="Enable collapse/expand behavior with toggle button",
    )
    resizable: bool = Field(
        default=False,
        description="Enable drag-to-resize (direction based on position)",
    )

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
        """Build complete toolbar HTML with collapsible/resizable support."""
        if not self.items:
            return ""

        # Build item HTMLs, passing toolbar component_id as parent context
        item_htmls = []
        for item in self.items:
            if isinstance(item, Div):
                item_htmls.append(item.build_html(parent_id=self.component_id))
            else:
                item_htmls.append(item.build_html())

        # Build container classes
        classes = ["pywry-toolbar", f"pywry-toolbar-{self.position}"]
        if self.class_name:
            classes.append(self.class_name)

        # Build attributes
        attrs = [
            f'class="{" ".join(classes)}"',
            f'id="{self.component_id}"',
            f'data-component-id="{self.component_id}"',
            f'data-position="{self.position}"',
        ]
        if self.collapsible:
            attrs.append('data-collapsible="true"')
            attrs.append('aria-expanded="true"')
        if self.resizable:
            attrs.append('data-resizable="true"')

        # Build collapse toggle button if collapsible
        toggle_html = ""
        if self.collapsible:
            toggle_html = (
                f'<button class="pywry-toolbar-toggle" type="button" '
                f'aria-label="Toggle toolbar" data-toolbar-id="{self.component_id}">'
                f'<span class="pywry-toggle-icon"></span>'
                f"</button>"
            )

        # Build resize handle if resizable
        resize_handle_html = ""
        if self.resizable:
            resize_handle_html = (
                f'<div class="pywry-resize-handle" data-toolbar-id="{self.component_id}"></div>'
            )

        # For 'inside' position, style goes on outer div (for absolute positioning: top, right, etc.)
        # For other positions, style goes on content wrapper (for flex alignment)
        outer_style = ""
        content_style = ""
        if self.style:
            if self.position == "inside":
                outer_style = f' style="{self.style}"'
            else:
                content_style = f' style="{self.style}"'

        content_html = (
            f'<div class="pywry-toolbar-content"{content_style}>{"".join(item_htmls)}</div>'
        )

        return f"<div {' '.join(attrs)}{outer_style}>{toggle_html}{content_html}{resize_handle_html}</div>"

    def collect_scripts(self) -> list[str]:
        """Collect scripts from toolbar and all nested Div children (depth-first).

        Toolbar script runs first, then Div scripts in item order.

        Returns
        -------
        list[str]
            List of script content strings.
        """
        scripts: list[str] = []

        # Toolbar script first (parent context available to children)
        if self.script:
            if isinstance(self.script, Path) or (
                isinstance(self.script, str)
                and not self.script.strip().startswith(
                    (
                        "(",
                        "{",
                        "function",
                        "//",
                        "/*",
                        "var ",
                        "let ",
                        "const ",
                        "if ",
                        "for ",
                        "while ",
                    )
                )
            ):
                script_path = Path(self.script) if isinstance(self.script, str) else self.script
                if script_path.exists():
                    scripts.append(script_path.read_text(encoding="utf-8"))
                else:
                    scripts.append(str(self.script))
            else:
                scripts.append(str(self.script))

        # Children's scripts (depth-first)
        for item in self.items:
            if isinstance(item, Div):
                scripts.extend(item.collect_scripts())

        return scripts

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
            "class_name": self.class_name,
            "collapsible": self.collapsible,
            "resizable": self.resizable,
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
    "slider": SliderInput,
    "range": RangeInput,
    "div": Div,
}


# =============================================================================
# Helper Functions for Building Toolbars
# =============================================================================


def build_toolbar_html(toolbar: Toolbar | dict[str, Any]) -> str:
    """Build HTML for a single toolbar.

    Parameters
    ----------
    toolbar : Toolbar or dict
        Toolbar configuration.

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


# =============================================================================
# Toolbar JavaScript (for dropdown/select interactivity)
# =============================================================================

# CENTRALIZED: Load toolbar handlers from single source file
# The same JavaScript is used by widget.py for anywidget rendering


@lru_cache(maxsize=1)
def _get_toolbar_handlers_js() -> str:
    """Load centralized toolbar handler JavaScript.

    This is the SINGLE SOURCE OF TRUTH for toolbar interaction JavaScript.
    Used by both native windows (via get_toolbar_script) and widgets.
    """
    toolbar_handlers_path = _SRC_DIR / "toolbar-handlers.js"
    if not toolbar_handlers_path.exists():
        raise RuntimeError(f"Toolbar handlers JS not found: {toolbar_handlers_path}")
    return toolbar_handlers_path.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _get_toolbar_script_content() -> str:
    """Build the complete toolbar script for native windows.

    Wraps the centralized handlers in an IIFE with initialization code
    suitable for standalone HTML pages (native windows).
    """
    handlers_js = _get_toolbar_handlers_js()

    # Wrap in IIFE with native window initialization
    # Expose initToolbarHandlers globally so it can be called after content injection
    return f"""
(function() {{
    // Load centralized toolbar handlers FIRST
    {handlers_js}

    // Expose globally for re-initialization after content injection
    window.initToolbarHandlers = initToolbarHandlers;

    // Guard: only setup pywry and initial call once per page
    if (window.__PYWRY_TOOLBAR_INIT__) return;
    window.__PYWRY_TOOLBAR_INIT__ = true;

    // Ensure window.pywry exists for native windows
    // IMPORTANT: Use pyInvoke to send events to Python, not event.emit which is frontend-only
    window.pywry = window.pywry || {{
        _handlers: {{}},
        on: function(event, handler) {{
            this._handlers[event] = this._handlers[event] || [];
            this._handlers[event].push(handler);
        }},
        emit: function(eventType, data) {{
            // Send event to Python via pyInvoke (the correct IPC mechanism)
            var payload = {{
                label: window.__PYWRY_LABEL__ || 'main',
                event_type: eventType,
                data: data || {{}}
            }};
            if (window.__TAURI__ && window.__TAURI__.pytauri && window.__TAURI__.pytauri.pyInvoke) {{
                window.__TAURI__.pytauri.pyInvoke('pywry_event', payload).catch(function(e) {{
                    console.error('[PyWry Toolbar] emit error:', e);
                }});
            }}
            // Also fire local handlers for immediate UI feedback
            this._fire(eventType, data);
        }},
        _fire: function(event, data) {{
            var handlers = this._handlers[event] || [];
            handlers.forEach(function(h) {{ h(data); }});
        }}
    }};

    // Initialize when DOM is ready (this runs on empty DOM initially, will be called again after content)
    function initNativeToolbars() {{
        if (typeof initToolbarHandlers === 'function') {{
            initToolbarHandlers(document, window.pywry);
        }}
    }}

    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initNativeToolbars);
    }} else {{
        initNativeToolbars();
    }}
}})();
"""


def get_toolbar_script(*, with_script_tag: bool = True) -> str:
    """Get the JavaScript required for toolbar interactivity.

    This script handles:
    - Dropdown (Select) open/close and option selection
    - Button click events
    - Text/Number/Date input with debouncing
    - Slider/Range input with live updates
    - MultiSelect checkbox handling
    - Dynamic toolbar updates via toolbar:set_value event

    Parameters
    ----------
    with_script_tag : bool, default True
        If True, wrap in <script> tags. If False, return raw JavaScript
        (for embedding inside an existing script block).

    Returns
    -------
    str
        JavaScript code or script tag containing toolbar JavaScript.
        Safe to include multiple times (has internal guard).
    """
    script_content = _get_toolbar_script_content()
    if with_script_tag:
        return f"<script>{script_content}</script>"
    return script_content


def wrap_content_with_toolbars(
    content: str,
    toolbars: Sequence[dict[str, Any] | Toolbar] | None = None,
    extra_top_html: str = "",
) -> str:
    """Wrap content with toolbar layout wrappers.

    This is THE SINGLE source of truth for toolbar layout structure.
    All rendering paths (show, show_plotly, show_dataframe) MUST use this.

    Layout structure (outside in):
        HEADER (full width)
        LEFT | TOP / CONTENT / BOTTOM | RIGHT
        FOOTER (full width)

    This means:
    - HEADER/FOOTER span full width at top/bottom
    - LEFT/RIGHT extend full height between header and footer
    - TOP/BOTTOM are inside the left/right columns
    - Content is centered in remaining space

    Parameters
    ----------
    content : str
        The inner content HTML (raw, will be wrapped in pywry-content).
    toolbars : list
        List of toolbar configurations (Toolbar models or dicts).
    extra_top_html : str
        Additional HTML to prepend to top toolbar area (e.g., custom header).

    Returns
    -------
    str
        Content wrapped with appropriate layout divs.
    """
    if not toolbars and not extra_top_html:
        # No toolbars - just wrap in pywry-content
        return f"<div class='pywry-content'>{content}</div>"

    # Group toolbars by position
    toolbar_html: dict[str, list[str]] = {
        "header": [],
        "footer": [],
        "top": [],
        "bottom": [],
        "left": [],
        "right": [],
        "inside": [],
    }

    if toolbars:
        for toolbar_cfg in toolbars:
            # Handle both Toolbar Pydantic models and dict configs
            if isinstance(toolbar_cfg, Toolbar):
                pos = toolbar_cfg.position
                html_str = toolbar_cfg.build_html()
            elif hasattr(toolbar_cfg, "build_html"):
                pos = getattr(toolbar_cfg, "position", "top")
                html_str = toolbar_cfg.build_html()
            else:
                pos = toolbar_cfg.get("position", "top")
                items = toolbar_cfg.get("items", [])
                html_str = Toolbar(position=pos, items=items).build_html() if items else ""

            if html_str and pos in toolbar_html:
                toolbar_html[pos].append(html_str)

    # Build HTML strings for each position
    header_str = "".join(toolbar_html["header"])
    footer_str = "".join(toolbar_html["footer"])
    top_str = extra_top_html + "".join(toolbar_html["top"])
    bottom_str = "".join(toolbar_html["bottom"])
    left_str = "".join(toolbar_html["left"])
    right_str = "".join(toolbar_html["right"])
    inside_str = "".join(toolbar_html["inside"])

    # Layer wrappers from inside out:
    # content -> inside -> top/bottom -> left/right -> header/footer
    # This makes LEFT/RIGHT extend full height between HEADER/FOOTER

    # Wrap content in pywry-content
    wrapped = f"<div class='pywry-content'>{content}</div>"

    # Inside (overlay)
    if inside_str:
        wrapped = f"<div class='pywry-wrapper-inside'>{inside_str}{wrapped}</div>"

    # Top/Bottom (inside left/right)
    if top_str or bottom_str:
        wrapped = f"<div class='pywry-wrapper-top'>{top_str}{wrapped}{bottom_str}</div>"

    # Left/Right (extend full height)
    if left_str or right_str:
        wrapped = f"<div class='pywry-wrapper-left'>{left_str}{wrapped}{right_str}</div>"

    # Header/Footer (outermost, full width)
    if header_str or footer_str:
        wrapped = f"<div class='pywry-wrapper-header'>{header_str}{wrapped}{footer_str}</div>"

    return wrapped
