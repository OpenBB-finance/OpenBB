# pylint: disable=too-many-lines,unused-argument
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
            Button(label="Refresh", event="app:refresh", data={"force": True}),
            Select(
                label="View:",
                event="view:change",
                options=[Option(label="Table", value="table"), Option(label="Chart", value="chart")],
                selected="table",
            ),
        ],
    )

    # Use in app.show()
    app.show(content, toolbars=[toolbar])
"""

from __future__ import annotations

import html
import json
import re
import uuid

from collections.abc import Callable, Sequence
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)


# Directory containing frontend source files
_SRC_DIR = Path(__file__).parent / "frontend" / "src"


# =============================================================================
# Secret Registry - Stores secrets by component_id for reveal/copy handlers
# =============================================================================

# Maps component_id -> SecretStr (weak refs to allow cleanup)
_SECRET_REGISTRY: dict[str, SecretStr] = {}

# Maps event -> custom handler (for user overrides)
_SECRET_HANDLERS: dict[str, Callable[..., str | None]] = {}


def register_secret(component_id: str, secret: SecretStr) -> None:
    """Register a secret value for a SecretInput component.

    Called automatically when SecretInput is rendered. The secret can then
    be retrieved by reveal/copy handlers.

    Parameters
    ----------
    component_id : str
        The unique component ID of the SecretInput.
    secret : SecretStr
        The secret value to store.
    """
    _SECRET_REGISTRY[component_id] = secret


def get_secret(component_id: str) -> str | None:
    """Retrieve a secret value by component ID.

    Parameters
    ----------
    component_id : str
        The unique component ID of the SecretInput.

    Returns
    -------
    str | None
        The secret value, or None if not found.
    """
    secret = _SECRET_REGISTRY.get(component_id)
    if secret:
        return secret.get_secret_value()
    return None


def clear_secret(component_id: str) -> None:
    """Remove a secret from the registry.

    Parameters
    ----------
    component_id : str
        The unique component ID of the SecretInput.
    """
    _SECRET_REGISTRY.pop(component_id, None)


def encode_secret(value: str) -> str:
    """Base64 encode a secret for transit obfuscation.

    Parameters
    ----------
    value : str
        The secret value to encode.

    Returns
    -------
    str
        Base64 encoded string.
    """
    import base64

    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def decode_secret(encoded: str) -> str:
    """Decode a base64-encoded secret from transit.

    Parameters
    ----------
    encoded : str
        The base64 encoded secret.

    Returns
    -------
    str
        The decoded secret value.
    """
    import base64

    return base64.b64decode(encoded.encode("ascii")).decode("utf-8")


def set_secret_handler(
    event: str, handler: Callable[[dict[str, Any]], str | None]
) -> None:
    """Set a custom handler for secret reveal/copy events.

    Use this to add custom validation, authentication, or logging before
    returning secrets. The handler receives the event data and should return
    the secret string or None to deny access.

    Parameters
    ----------
    event : str
        The event type (e.g., "settings:api-key:reveal").
    handler : Callable
        Function that takes event data dict and returns secret or None.

    Example
    -------
        def my_reveal_handler(data: dict) -> str | None:
            # Custom auth check
            if not is_authenticated():
                return None
            return get_secret(data["componentId"])

        set_secret_handler("settings:api-key:reveal", my_reveal_handler)
    """
    _SECRET_HANDLERS[event] = handler


def get_secret_handler(event: str) -> Callable[[dict[str, Any]], str | None] | None:
    """Get a custom handler for a secret event.

    Parameters
    ----------
    event : str
        The event type.

    Returns
    -------
    Callable | None
        The custom handler, or None if using default.
    """
    return _SECRET_HANDLERS.get(event)


ToolbarPosition = Literal[
    "header", "footer", "top", "bottom", "left", "right", "inside"
]
ItemType = Literal[
    "button",
    "select",
    "multiselect",
    "text",
    "textarea",
    "search",
    "number",
    "date",
    "slider",
    "range",
    "toggle",
    "checkbox",
    "radio",
    "div",
    "marquee",
]


# Event pattern: namespace:event-name (e.g., "app:refresh", "view:change")
# Namespace: starts with letter, alphanumeric only
# Event name: starts with letter, alphanumeric + underscores + hyphens
EVENT_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9]*:[a-zA-Z][a-zA-Z0-9_-]*$")

# Reserved namespaces that users should not use
RESERVED_NAMESPACES = frozenset({"pywry", "plotly", "grid"})

# Exceptions to reserved namespaces
ALLOWED_RESERVED_PATTERNS = [
    "plotly:modebar-",
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
            object.__setattr__(
                self, "component_id", _generate_component_id(component_type)
            )
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
        """Build data-tooltip attribute for custom tooltip if description is set."""
        if self.description:
            return f' data-tooltip="{html.escape(self.description)}"'
        return ""

    def build_html(self) -> str:
        """Build HTML for this toolbar item. Override in subclasses."""
        raise NotImplementedError


class Button(ToolbarItem):
    """A clickable button that emits an event with optional data payload.

    Parameters
    ----------
        variant: Button style variant:
            - "primary" (theme-aware: light bg in dark mode, accent in light mode)
            - "secondary" (subtle background, theme-aware)
            - "neutral" (blue)
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
        Button(label="Cancel", event="app:cancel", variant="secondary")
        Button(label="⚙", event="app:settings", variant="icon")
        Button(label="Submit", event="form:submit", variant="neutral", size="lg")
    """

    type: Literal["button"] = "button"
    data: dict[str, Any] = Field(default_factory=dict)
    variant: Literal[
        "primary",
        "secondary",
        "neutral",
        "ghost",
        "outline",
        "danger",
        "warning",
        "icon",
    ] = "primary"
    size: Literal["xs", "sm", "lg", "xl"] | None = None

    def build_html(self) -> str:
        """Build button HTML."""
        variant_class = (
            f" pywry-btn-{self.variant}" if self.variant != "primary" else ""
        )
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


class Select(ToolbarItem):
    """A single-select dropdown with optional search.

    Emits: {value: <selected_value>}

    Attributes
    ----------
        options: List of Option items for the dropdown
        selected: Currently selected value
        searchable: Enable search input to filter options (default: False)

    Example:
        Select(
            label="Theme:",
            event="theme:change",
            options=[Option(label="Dark", value="dark"), Option(label="Light", value="light")],
            selected="dark",
            searchable=True,
        )
    """

    type: Literal["select"] = "select"
    options: list[Option] = Field(default_factory=list)
    selected: str = ""
    searchable: bool = Field(
        default=False,
        description="Enable search input to filter dropdown options",
    )

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
        searchable_class = " pywry-searchable" if self.searchable else ""
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

        # Search header (if searchable)
        search_header = ""
        if self.searchable:
            search_input = SearchInput(placeholder="Search...")
            search_header = f'<div class="pywry-select-header">{search_input.build_inline_html()}</div>'

        # Custom dropdown structure
        dropdown_html = (
            f'<div class="pywry-dropdown{searchable_class}{disabled_attr}" id="{self.component_id}" '
            f'data-event="{self.event}"{title_attr}>'
            f'<div class="pywry-dropdown-selected">'
            f'<span class="pywry-dropdown-text">{html.escape(str(selected_label))}</span>'
            f'<span class="pywry-dropdown-arrow"></span>'
            f"</div>"
            f'<div class="pywry-dropdown-menu">'
            f"{search_header}"
            f'<div class="pywry-select-options">{options_html}</div>'
            f"</div>"
            f"</div>"
        )

        if self.label:
            return (
                f'<div class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>'
                f"{dropdown_html}</div>"
            )
        return (
            f'<div style="{self.style}">{dropdown_html}</div>'
            if self.style
            else dropdown_html
        )


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
        selected_labels = [
            opt.label for opt in self.options if str(opt.value) in selected_set
        ]

        if len(selected_labels) == 0:
            display_text = "Select..."
        elif len(selected_labels) <= 2:
            display_text = ", ".join(selected_labels)
        else:
            display_text = f"{len(selected_labels)} selected"

        # Separate options: selected first, then unselected
        selected_opts = [opt for opt in self.options if str(opt.value) in selected_set]
        unselected_opts = [
            opt for opt in self.options if str(opt.value) not in selected_set
        ]
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

        # Header with search (using SearchInput) and select all/none buttons
        search_input = SearchInput(placeholder="Search...")
        header_html = (
            '<div class="pywry-multiselect-header">'
            f"{search_input.build_inline_html()}"
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
        return (
            f'<div style="{self.style}">{dropdown_html}</div>'
            if self.style
            else dropdown_html
        )


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


# SVG icons for secret input (14x14, feather-style)
_EYE_ICON_SVG = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>'
    '<circle cx="12" cy="12" r="3"/></svg>'
)
_EYE_OFF_ICON_SVG = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94'
    'M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>'
    '<line x1="1" y1="1" x2="23" y2="23"/></svg>'
)
_COPY_ICON_SVG = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>'
    '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>'
)
_CHECK_ICON_SVG = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<polyline points="20 6 9 17 4 12"/></svg>'
)

# Type alias for secret handler callable.
# Signature: (value, *, component_id, event, label, **metadata) -> str | None
#   - value: None for get operation, string for set operation
#   - component_id: unique ID for this component
#   - event: the event string
#   - label: optional label text
#   - metadata: additional attributes (e.g., data-* attributes)
SecretHandler = Callable[..., str | None]


class SecretInput(ToolbarItem):
    """A password/secret input field with visibility toggle and copy button.

    Displays a masked input by default with icons on the right side:
    - Eye icon to toggle visibility (requests secret from backend)
    - Copy icon to copy value to clipboard (requests secret from backend)

    Icons appear on hover/focus and input text is padded to not overlap them.

    SECURITY: The secret value is NEVER rendered in HTML. When the user clicks
    the show or copy buttons, JavaScript emits events to request the secret
    from the backend. The backend must handle these events and respond with
    the actual value. This ensures secrets are only transmitted on explicit
    user action and never embedded in the DOM.

    Events emitted:
    - `{event}` - On input change: {value, componentId}
    - `{event}:reveal` - On show click: {componentId} - backend should respond with secret
    - `{event}:copy` - On copy click: {componentId} - backend should respond with secret

    Attributes
    ----------
        value: Secret value stored as SecretStr (NEVER rendered in HTML)
        placeholder: Placeholder text shown when empty
        debounce: Milliseconds to debounce input events (default: 300)
        show_toggle: Show the visibility toggle button (default: True)
        show_copy: Show the copy to clipboard button (default: True)
        handler: Optional callable for custom secret storage.
            Signature: (value, *, component_id, event, label, **metadata) -> str | None
            - value: None to get the secret, string to set the secret
            - component_id: unique component ID for tracking
            - event: the event string
            - label: optional label text
            - metadata: additional attributes
            If not provided, uses internal SecretStr storage.

    Example:
        # Simple usage with internal storage:
        SecretInput(
            label="API Key:",
            event="settings:api_key",
            value="my-secret",
        )

        # Custom handler with component metadata:
        def api_key_handler(
            value: str | None,
            *,
            component_id: str,
            event: str,
            label: str | None = None,
            **metadata,
        ) -> str | None:
            if value is None:
                return secrets_manager.get(component_id)
            secrets_manager.set(component_id, value)
            return value

        SecretInput(
            event="settings:api_key",
            handler=api_key_handler,
        )
    """

    model_config = {"arbitrary_types_allowed": True}

    type: Literal["secret"] = "secret"
    value: SecretStr = SecretStr("")
    placeholder: str = ""
    debounce: int = Field(default=300, ge=0)
    show_toggle: bool = True
    show_copy: bool = True
    handler: SecretHandler | None = Field(default=None, exclude=True)
    # Explicit flag to indicate a value exists (e.g., in external vault)
    # If None, computed from value; if True/False, used directly
    value_exists: bool | None = Field(default=None)

    @field_validator("value", mode="before")
    @classmethod
    def _coerce_value_to_secret(cls, v: str | SecretStr) -> SecretStr:
        """Allow plain strings to be passed and convert to SecretStr."""
        if isinstance(v, SecretStr):
            return v
        return SecretStr(v) if v else SecretStr("")

    @property
    def has_value(self) -> bool:
        """Check if a secret value is set (without exposing it).

        Returns True if:
        - value_exists is explicitly True, OR
        - value_exists is None and internal value is non-empty
        """
        if self.value_exists is not None:
            return self.value_exists
        return bool(self.value.get_secret_value())

    def build_html(self) -> str:
        """Build secret input HTML with visibility toggle and copy button.

        SECURITY: The actual secret value is NEVER included in the HTML.
        When a value exists, a fixed mask (••••••••••••) is shown.
        Show/copy buttons emit events to request the real secret from the backend.
        Values are base64 encoded in transit for obfuscation.

        Edit mode:
        - Click on input or edit button to enter edit mode
        - Switches to a resizable textarea (no wrapping, no formatting)
        - Confirm with blur or Ctrl+Enter
        - Cancel with Escape (restores mask)
        - Only transmits on confirm, not during typing
        """
        disabled_attr = " disabled" if self.disabled else ""

        # Mask to show when value exists (12 bullet characters)
        mask_chars = "••••••••••••"

        # Display value: mask if value exists, empty otherwise
        display_value = mask_chars if self.has_value else ""
        has_value_attr = ' data-has-value="true"' if self.has_value else ""
        masked_attr = ' data-masked="true"' if self.has_value else ""

        # Edit mode handler - switches input to textarea with confirm/cancel buttons
        # Textarea: resizable, no wrap, no formatting, starts at input size
        # SVG icons for confirm (checkmark) and cancel (X)
        confirm_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
        cancel_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
        confirm_svg_escaped = html.escape(confirm_svg)
        cancel_svg_escaped = html.escape(cancel_svg)

        enter_edit_script = (
            f"(function(inp){{"
            f"if(inp.dataset.editing==='true')return;"
            f"inp.dataset.editing='true';"
            f"var rect=inp.getBoundingClientRect();"
            f"var wrapper=inp.closest('.pywry-secret-wrapper');"
            f"var actions=wrapper.querySelector('.pywry-secret-actions');"
            # Hide normal action buttons
            f"if(actions)actions.style.display='none';"
            f"var ta=document.createElement('textarea');"
            f"ta.id=inp.id+'_edit';"
            f"ta.className='pywry-input pywry-secret-textarea';"
            f"ta.placeholder=inp.placeholder;"
            f"ta.style.width=rect.width+'px';"
            f"ta.style.height=rect.height+'px';"
            f"ta.style.minWidth=rect.width+'px';"
            f"ta.style.minHeight=rect.height+'px';"
            f"ta.dataset.componentId='{self.component_id}';"
            f"ta.dataset.originalValue=inp.dataset.hasValue==='true'?'__HAS_VALUE__':'';"
            # Create confirm/cancel button container
            f"var editActions=document.createElement('span');"
            f"editActions.className='pywry-secret-actions pywry-secret-edit-actions';"
            f"editActions.style.opacity='1';editActions.style.pointerEvents='auto';"
            # Confirm button
            f"var confirmBtn=document.createElement('button');"
            f"confirmBtn.type='button';"
            f"confirmBtn.className='pywry-secret-btn pywry-secret-confirm';"
            f"confirmBtn.dataset.tooltip='Confirm (Ctrl+Enter)';"
            f"confirmBtn.innerHTML='{confirm_svg_escaped}';"
            f"confirmBtn.onclick=function(e){{e.stopPropagation();ta.blur();}};"
            # Cancel button
            f"var cancelBtn=document.createElement('button');"
            f"cancelBtn.type='button';"
            f"cancelBtn.className='pywry-secret-btn pywry-secret-cancel';"
            f"cancelBtn.dataset.tooltip='Cancel (Escape)';"
            f"cancelBtn.innerHTML='{cancel_svg_escaped}';"
            f"cancelBtn.onclick=function(e){{e.stopPropagation();ta._cancelled=true;ta.onblur();}};"
            f"editActions.appendChild(confirmBtn);"
            f"editActions.appendChild(cancelBtn);"
            # Confirm handler - blur
            f"ta.onblur=function(){{"
            f"if(ta._blurring)return;ta._blurring=true;"
            f"var val=ta._cancelled?null:ta.value;"
            f"if(val!==null){{"
            f"var encoded=btoa(unescape(encodeURIComponent(val)));"
            f"if(window.pywry&&window.pywry.emit){{"
            f"window.pywry.emit('{self.event}',{{value:encoded,encoded:true,componentId:'{self.component_id}'}});"
            f"}}"
            # Restore input with new mask state
            f"inp.dataset.hasValue=val?'true':'false';"
            f"inp.value=val?'{mask_chars}':'';"
            f"inp.dataset.masked=val?'true':'false';"
            f"}}"
            f"inp.dataset.editing='false';"
            f"ta.remove();editActions.remove();"
            f"inp.style.display='';"
            # Show normal action buttons again
            f"if(actions)actions.style.display='';"
            f"}};"
            # Keydown handler - Ctrl+Enter to confirm, Escape to cancel
            f"ta.onkeydown=function(e){{"
            f"if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){{"
            f"e.preventDefault();ta.blur();"
            f"}}else if(e.key==='Escape'){{"
            f"e.preventDefault();ta._cancelled=true;ta.onblur();"
            f"}}"
            f"}};"
            # Insert textarea and edit actions, hide input
            f"inp.style.display='none';"
            f"wrapper.insertBefore(ta,inp);"
            f"wrapper.appendChild(editActions);"
            f"ta.focus();"
            f"}})(this)"
        )

        # SECURITY: actual secret is NEVER in HTML - only mask or empty
        # SECURITY: actual secret is NEVER in HTML - only mask or empty
        # Input is readonly - users must click Edit button to modify
        # Cursor style indicates non-editable, data-tooltip provides styled instruction
        input_html = (
            f'<input type="password" class="pywry-input pywry-input-secret" '
            f'id="{self.component_id}" value="{display_value}"{masked_attr} '
            f'placeholder="{html.escape(self.placeholder)}" '
            f'autocomplete="off" spellcheck="false"{has_value_attr} '
            f'readonly data-tooltip="Click Edit button to modify"{disabled_attr}>'
        )

        # Build action buttons container
        buttons_html = ""

        # Edit button - enters edit mode
        edit_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>'
        edit_script = (
            f"var inp=document.getElementById('{self.component_id}');"
            f"{enter_edit_script.replace('(this)', '(inp)')}"
        )
        buttons_html += (
            f'<button type="button" class="pywry-secret-btn pywry-secret-edit" '
            f'data-tooltip="Edit value" onclick="{edit_script}">{edit_svg}</button>'
        )

        if self.show_copy:
            # Escape SVGs for data attributes
            copy_svg_escaped = html.escape(_COPY_ICON_SVG)
            check_svg_escaped = html.escape(_CHECK_ICON_SVG)
            # Register one-time handler for response, then emit request
            # Backend handles {event}:copy and dispatches {event}:copy-response with base64 {value}
            copy_script = (
                f"var btn=this;var cid='{self.component_id}';"
                f"var handler=function(d){{if(d.componentId===cid&&d.value){{"
                # Decode base64 response
                f"var secret=d.encoded?decodeURIComponent(escape(atob(d.value))):d.value;"
                f"navigator.clipboard.writeText(secret);"
                f"btn.innerHTML=btn.dataset.check;btn.classList.add('copied');"
                f"btn.dataset.tooltip='Copied!';"
                f"setTimeout(function(){{btn.innerHTML=btn.dataset.copy;btn.classList.remove('copied');btn.dataset.tooltip='Copy to clipboard';}},1500);"
                f"window.pywry.off('{self.event}:copy-response',handler);"
                f"}}}};"
                f"window.pywry.on('{self.event}:copy-response',handler);"
                f"window.pywry.emit('{self.event}:copy',{{componentId:cid}});"
            )
            buttons_html += (
                f'<button type="button" class="pywry-secret-btn pywry-secret-copy" '
                f'data-tooltip="Copy to clipboard" data-copy="{copy_svg_escaped}" data-check="{check_svg_escaped}" '
                f'onclick="{copy_script}">{_COPY_ICON_SVG}</button>'
            )

        if self.show_toggle:
            # Escape SVGs for data attributes
            eye_svg_escaped = html.escape(_EYE_ICON_SVG)
            eye_off_svg_escaped = html.escape(_EYE_OFF_ICON_SVG)
            # Register one-time handler for response, then emit request
            # Backend handles {event}:reveal and dispatches {event}:reveal-response with base64 {value}
            # Track revealed secrets for cleanup on page unload
            # When hiding, restore mask if we were showing a stored value (not user-typed)
            toggle_script = (
                f"var btn=this;var inp=document.getElementById('{self.component_id}');var cid='{self.component_id}';"
                f"var isHidden=inp.type==='password';"
                f"var MASK='••••••••••••';"
                f"if(isHidden){{"
                f"var handler=function(d){{if(d.componentId===cid){{"
                # Decode base64 response
                f"var secret=d.encoded?decodeURIComponent(escape(atob(d.value||''))):d.value||'';"
                f"inp.value=secret;inp.type='text';inp.dataset.masked='false';"
                # Track revealed secret for cleanup on unload
                f"window.pywry._revealedSecrets=window.pywry._revealedSecrets||{{}};window.pywry._revealedSecrets[cid]=true;"
                f"btn.innerHTML=btn.dataset.hide;btn.dataset.tooltip='Hide value';"
                f"window.pywry.off('{self.event}:reveal-response',handler);"
                f"}}}};"
                f"window.pywry.on('{self.event}:reveal-response',handler);"
                f"window.pywry.emit('{self.event}:reveal',{{componentId:cid}});"
                f"}}else{{"
                # When hiding: restore mask if has_value, otherwise empty
                f"inp.type='password';"
                f"inp.value=inp.dataset.hasValue==='true'?MASK:'';"
                f"inp.dataset.masked=inp.dataset.hasValue==='true'?'true':'false';"
                # Remove from revealed tracking
                f"if(window.pywry._revealedSecrets)delete window.pywry._revealedSecrets[cid];"
                f"btn.innerHTML=btn.dataset.show;btn.dataset.tooltip='Show value';"
                f"}}"
            )
            buttons_html += (
                f'<button type="button" class="pywry-secret-btn pywry-secret-toggle" '
                f'data-tooltip="Show value" data-show="{eye_svg_escaped}" data-hide="{eye_off_svg_escaped}" '
                f'onclick="{toggle_script}">{_EYE_ICON_SVG}</button>'
            )

        if buttons_html:
            input_wrapper = (
                f'<span class="pywry-secret-wrapper">'
                f"{input_html}"
                f'<span class="pywry-secret-actions">{buttons_html}</span>'
                f"</span>"
            )
        else:
            input_wrapper = input_html

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>'
                f"{input_wrapper}</span>"
            )
        return input_wrapper

    def register(self) -> None:
        """Register this SecretInput in the secret registry.

        Called automatically by Toolbar when building HTML.
        If a custom handler is provided, it's registered for reveal/copy events.
        Otherwise, the internal value is registered for retrieval.
        """
        if self.handler is not None:
            # Register custom handler for both reveal and copy events
            set_secret_handler(self.get_reveal_event(), self._wrap_handler_for_get)
            set_secret_handler(self.get_copy_event(), self._wrap_handler_for_get)
        elif self.has_value:
            register_secret(self.component_id, self.value)

    def _wrap_handler_for_get(self, _data: dict[str, Any]) -> str | None:
        """Wrap the handler callable for get operations (reveal/copy).

        Parameters
        ----------
        _data : dict[str, Any]
            Event data from the frontend (unused, required for handler signature).

        Returns
        -------
        str | None
            The secret value, or None if not available.
        """
        if self.handler is not None:
            return self.handler(
                None,  # Get mode
                component_id=self.component_id,
                event=self.event,
                label=self.label,
            )
        return get_secret(self.component_id)

    def update_secret(self, new_value: str | SecretStr, encoded: bool = False) -> None:
        """Update the stored secret value.

        Use this when receiving a new value from user input.
        If a custom handler is configured, it will be called to store the value.

        Parameters
        ----------
        new_value : str | SecretStr
            The new secret value. If encoded=True and this is a string,
            it will be base64-decoded first.
        encoded : bool, default False
            Whether the value is base64-encoded (for transit obfuscation).
        """
        # Decode if transmitted with base64 obfuscation
        if isinstance(new_value, str) and encoded:
            new_value = decode_secret(new_value)

        # Convert to plain string for handler
        plain_value = (
            new_value.get_secret_value()
            if isinstance(new_value, SecretStr)
            else new_value
        )

        # If custom handler, call it with the value (set mode) and metadata
        if self.handler is not None:
            self.handler(
                plain_value,
                component_id=self.component_id,
                event=self.event,
                label=self.label,
            )
        else:
            # Update internal value and registry
            secret_value = (
                new_value if isinstance(new_value, SecretStr) else SecretStr(new_value)
            )
            object.__setattr__(self, "value", secret_value)
            register_secret(self.component_id, secret_value)

    def get_reveal_event(self) -> str:
        """Get the event type for reveal requests."""
        return f"{self.event}:reveal"

    def get_reveal_response_event(self) -> str:
        """Get the event type for reveal responses."""
        return f"{self.event}:reveal-response"

    def get_copy_event(self) -> str:
        """Get the event type for copy requests."""
        return f"{self.event}:copy"

    def get_copy_response_event(self) -> str:
        """Get the event type for copy responses."""
        return f"{self.event}:copy-response"

    def get_secret_value(self) -> str | None:
        """Get the current secret value.

        If a custom handler is configured, calls handler with metadata.
        Otherwise, returns the internal value or from the registry.

        Returns
        -------
        str | None
            The secret value, or None if not set.
        """
        if self.handler is not None:
            return self.handler(
                None,  # Get mode
                component_id=self.component_id,
                event=self.event,
                label=self.label,
            )
        if self.has_value:
            return self.value.get_secret_value()
        return get_secret(self.component_id)


class TextArea(ToolbarItem):
    """A multi-line text area that supports resizing and paste.

    Emits: {value: <text_value>}

    The textarea is resizable in all directions by default. Use the resize
    attribute to control resize behavior.

    Attributes
    ----------
        value: Initial text content
        placeholder: Placeholder text shown when empty
        debounce: Milliseconds to debounce input events (default: 300)
        rows: Initial number of visible text rows (default: 3)
        cols: Initial number of visible columns (default: 40)
        resize: CSS resize behavior ("both", "horizontal", "vertical", "none")
        min_height: Minimum height CSS value (e.g., "50px")
        max_height: Maximum height CSS value (e.g., "500px")
        min_width: Minimum width CSS value (e.g., "100px")
        max_width: Maximum width CSS value (e.g., "100%")

    Example:
        TextArea(
            label="Notes:",
            event="notes:update",
            placeholder="Enter your notes here...",
            rows=5,
            resize="vertical",
        )
    """

    type: Literal["textarea"] = "textarea"
    value: str = ""
    placeholder: str = ""
    debounce: int = Field(default=300, ge=0)
    rows: int = Field(default=3, ge=1)
    cols: int = Field(default=40, ge=1)
    resize: Literal["both", "horizontal", "vertical", "none"] = "both"
    min_height: str = ""
    max_height: str = ""
    min_width: str = ""
    max_width: str = ""

    def build_html(self) -> str:
        """Build textarea HTML."""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()

        # Build inline style for resize constraints
        style_parts = [f"resize: {self.resize}"]
        if self.min_height:
            style_parts.append(f"min-height: {self.min_height}")
        if self.max_height:
            style_parts.append(f"max-height: {self.max_height}")
        if self.min_width:
            style_parts.append(f"min-width: {self.min_width}")
        if self.max_width:
            style_parts.append(f"max-width: {self.max_width}")
        if self.style:
            style_parts.append(self.style)
        inline_style = "; ".join(style_parts)

        # Debounced input handler
        oninput = (
            f"clearTimeout(this._debounce); "
            f"var _el = this; "
            f"this._debounce = setTimeout(() => {{ "
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', {{value: _el.value, componentId: '{self.component_id}'}}, _el); "
            f"}} }}, {self.debounce});"
        )

        textarea_html = (
            f'<textarea class="pywry-input pywry-textarea" '
            f'id="{self.component_id}" '
            f'rows="{self.rows}" cols="{self.cols}" '
            f'placeholder="{html.escape(self.placeholder)}" '
            f'style="{html.escape(inline_style)}" '
            f'oninput="{oninput}"{title_attr}{disabled_attr}>'
            f"{html.escape(self.value)}</textarea>"
        )

        if self.label:
            return (
                f'<div class="pywry-input-group pywry-textarea-group">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>'
                f"{textarea_html}</div>"
            )
        return textarea_html


# SVG magnifying glass icon (circle top-left, handle pointing down-right)
# Uses stroke="currentColor" for theme-aware coloring via CSS
_SEARCH_ICON_SVG = (
    '<svg class="pywry-search-icon" width="14" height="14" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round"><circle cx="10" cy="10" r="7"/>'
    '<line x1="15" y1="15" x2="21" y2="21"/></svg>'
)


class SearchInput(ToolbarItem):
    """A search input field with magnifying glass icon and debounced events.

    Includes a muted theme-aware search icon on the left. Browser behaviors
    (spellcheck, autocomplete, autocorrect, autocapitalize) are disabled by
    default for cleaner search/filter UX.

    Emits: {value: <search_query>}

    Attributes
    ----------
        value: Current search text value
        placeholder: Placeholder text (default: "Search...")
        debounce: Milliseconds to wait before emitting (default: 300)
        spellcheck: Enable browser spell checking (default: False)
        autocomplete: Browser autocomplete behavior (default: "off")
        autocorrect: Enable browser auto-correction (default: "off")
        autocapitalize: Control mobile keyboard capitalization (default: "off")

    Example:
        SearchInput(
            label="Filter:",
            event="filter:search",
            placeholder="Type to filter...",
            debounce=200,
        )
    """

    type: Literal["search"] = "search"
    value: str = ""
    placeholder: str = "Search..."
    debounce: int = Field(default=300, ge=0)

    # Browser behavior controls - disabled by default for search/filter inputs
    spellcheck: bool = Field(
        default=False,
        description="Enable browser spell checking (shows red underlines)",
    )
    autocomplete: str = Field(
        default="off",
        description="Browser autocomplete behavior ('off', 'on', or specific tokens)",
    )
    autocorrect: Literal["on", "off"] = Field(
        default="off",
        description="Enable browser auto-correction (Safari/iOS)",
    )
    autocapitalize: Literal["off", "none", "on", "sentences", "words", "characters"] = (
        Field(
            default="off",
            description="Control capitalization on mobile keyboards",
        )
    )

    def build_html(self) -> str:
        """Build search input HTML with icon."""
        disabled_attr = " disabled" if self.disabled else ""
        title_attr = self._build_title_attr()

        # Browser behavior attributes
        browser_attrs = (
            f' spellcheck="{str(self.spellcheck).lower()}"'
            f' autocomplete="{html.escape(self.autocomplete)}"'
            f' autocorrect="{self.autocorrect}"'
            f' autocapitalize="{self.autocapitalize}"'
        )

        oninput = (
            f"clearTimeout(this._debounce); "
            f"var _el = this; "
            f"this._debounce = setTimeout(() => {{ "
            f"if (window.pywry && window.pywry.emit) {{ "
            f"window.pywry.emit('{self.event}', {{value: _el.value, componentId: '{self.component_id}'}}, _el); "
            f"}} }}, {self.debounce});"
        )

        # Input with icon wrapper
        input_html = (
            f'<div class="pywry-search-wrapper">'
            f"{_SEARCH_ICON_SVG}"
            f'<input type="text" class="pywry-input pywry-search-input" '
            f'id="{self.component_id}" value="{html.escape(self.value)}" '
            f'placeholder="{html.escape(self.placeholder)}" '
            f'oninput="{oninput}"{browser_attrs}{title_attr}{disabled_attr}>'
            f"</div>"
        )

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{input_html}</span>'
            )
        return input_html

    def build_inline_html(self) -> str:
        """Build inline search input HTML for embedding in dropdowns.

        Returns just the wrapper+icon+input without label, optimized for
        use inside Select/MultiSelect dropdown headers.
        """
        # Browser behavior attributes
        browser_attrs = (
            f' spellcheck="{str(self.spellcheck).lower()}"'
            f' autocomplete="{html.escape(self.autocomplete)}"'
            f' autocorrect="{self.autocorrect}"'
            f' autocapitalize="{self.autocapitalize}"'
        )

        return (
            f'<div class="pywry-search-wrapper pywry-search-inline">'
            f"{_SEARCH_ICON_SVG}"
            f'<input type="text" class="pywry-input pywry-search-input" '
            f'placeholder="{html.escape(self.placeholder)}"{browser_attrs}>'
            f"</div>"
        )


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
        wrapper_html = (
            f'<span class="pywry-number-wrapper">{input_html}{spinner_html}</span>'
        )

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{wrapper_html}</span>'
            )
        return wrapper_html


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

        attrs = [
            f'id="{self.component_id}"',
            f'data-event="{self.event}"',
            'class="pywry-input pywry-date-input"',
        ]
        if self.value:
            attrs.append(f'value="{html.escape(self.value)}"')
        if self.min:
            attrs.append(f'min="{html.escape(self.min)}"')
        if self.max:
            attrs.append(f'max="{html.escape(self.max)}"')

        input_html = f'<input type="date" {" ".join(attrs)}{disabled_attr}>'

        if self.label:
            return (
                f'<span class="pywry-input-group pywry-input-inline" style="{self.style}">'
                f'<span class="pywry-input-label">{html.escape(self.label)}</span>{input_html}</span>'
            )
        return input_html


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
        return (
            f'<span style="{self.style}">{radio_html}</span>'
            if self.style
            else radio_html
        )


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
            active_class = (
                " pywry-tab-active" if str(opt.value) == self.selected else ""
            )
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
            f'<span style="{self.style}">{tab_group_html}</span>'
            if self.style
            else tab_group_html
        )


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
                script_path = (
                    Path(self.script) if isinstance(self.script, str) else self.script
                )
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


class TickerItem(BaseModel):
    """A single updatable item within a Marquee (e.g., stock price, metric).

    This is a lightweight helper for creating spans with `data-ticker` attributes
    that can be individually updated via `toolbar:marquee-set-item` events.
    Since marquee content is duplicated for seamless scrolling, updates target
    ALL matching `data-ticker` elements.

    NOT a full ToolbarItem - this is a content helper for use inside Marquee.

    Parameters
    ----------
        ticker : str
            Unique identifier for this item (e.g., "AAPL", "BTC", "cpu-usage").
            Used as `data-ticker` attribute for targeting updates.
        text : str
            Initial text content to display.
        html : str
            Initial HTML content (alternative to text for rich content).
        class_name : str
            Additional CSS classes for styling.
        style : str
            Inline CSS styles.

    Example:
        # Create ticker items for a stock marquee
        items = [
            TickerItem(ticker="AAPL", text="AAPL $185.50", class_name="stock-up"),
            TickerItem(ticker="GOOGL", text="GOOGL $142.20"),
            TickerItem(ticker="MSFT", text="MSFT $415.80", class_name="stock-down"),
        ]
        marquee = Marquee(
            text=" • ".join(item.build_html() for item in items),
            speed=20,
        )

        # Later, update individual prices:
        event, data = items[0].update_payload(
            text="AAPL $186.25",
            class_add="stock-up",
            class_remove="stock-down"
        )
        widget.emit(event, data)
    """

    ticker: str = Field(
        ...,
        description="Unique identifier for targeting updates (data-ticker attribute)",
    )
    text: str = ""
    html: str = ""
    class_name: str = ""
    style: str = ""

    def build_html(self) -> str:
        """Build HTML span with data-ticker attribute.

        Returns
        -------
        str
            HTML span element with data-ticker for update targeting.
        """
        attrs = [f'data-ticker="{html.escape(self.ticker, quote=True)}"']
        classes = ["pywry-ticker-item"]
        if self.class_name:
            classes.append(self.class_name)
        attrs.append(f'class="{" ".join(classes)}"')
        if self.style:
            attrs.append(f'style="{self.style}"')

        content = self.html if self.html else html.escape(self.text)
        return f"<span {' '.join(attrs)}>{content}</span>"

    def update_payload(
        self,
        text: str | None = None,
        html_content: str | None = None,
        styles: dict[str, str] | None = None,
        class_add: str | list[str] | None = None,
        class_remove: str | list[str] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Generate event name and payload for dynamic item updates.

        Use with widget.emit() to update this ticker item's content/styles.
        Updates ALL elements matching this ticker (handles duplicated marquee content).

        Parameters
        ----------
        text : str | None
            New plain text content.
        html_content : str | None
            New HTML content (use instead of text for rich content).
        styles : dict[str, str] | None
            CSS styles to apply (e.g., {"color": "green", "fontWeight": "bold"}).
        class_add : str | list[str] | None
            CSS class(es) to add.
        class_remove : str | list[str] | None
            CSS class(es) to remove.

        Returns
        -------
        tuple[str, dict[str, Any]]
            Event name and payload dict for widget.emit().

        Example
        -------
            item = TickerItem(ticker="AAPL", text="AAPL $185.50")
            # Price went up - update with green color
            event, data = item.update_payload(
                text="AAPL $186.25 ▲",
                styles={"color": "#22c55e"},
                class_add="stock-up",
                class_remove="stock-down"
            )
            widget.emit(event, data)
        """
        payload: dict[str, Any] = {"ticker": self.ticker}
        if text is not None:
            payload["text"] = text
        if html_content is not None:
            payload["html"] = html_content
        if styles is not None:
            payload["styles"] = styles
        if class_add is not None:
            payload["class_add"] = class_add
        if class_remove is not None:
            payload["class_remove"] = class_remove
        return ("toolbar:marquee-set-item", payload)


class Marquee(ToolbarItem):
    """A scrolling text/content ticker component using CSS animations.

    Displays content that scrolls horizontally or vertically across the container.
    Useful for news tickers, announcements, or any content that should scroll continuously.

    Uses CSS animations instead of the deprecated <marquee> HTML element for
    better browser compatibility, performance, and accessibility.

    Emits: {value: <text>, componentId: <id>} when clicked (if clickable=True)

    Dynamic Updates
    ---------------
    Use `toolbar:marquee-set-content` to update content from Python:

        # Update text content
        widget.emit("toolbar:marquee-set-content", {
            "id": marquee.component_id,
            "text": "New scrolling text!"
        })

        # Update with HTML content
        widget.emit("toolbar:marquee-set-content", {
            "id": marquee.component_id,
            "html": "<b>Bold</b> and <em>italic</em> text"
        })

        # Change speed dynamically
        widget.emit("toolbar:marquee-set-content", {
            "id": marquee.component_id,
            "speed": 10  # seconds per cycle
        })

        # Pause/resume animation
        widget.emit("toolbar:marquee-set-content", {
            "id": marquee.component_id,
            "paused": True  # or False to resume
        })

    Attributes
    ----------
        text: The text content to scroll. Can include simple inline HTML (<b>, <em>, <span>).
        speed: Animation duration in seconds for one complete scroll cycle.
            Lower values = faster scrolling. Default: 15 seconds.
        direction: Scroll direction.
            - "left" (default): Content moves from right to left
            - "right": Content moves from left to right
            - "up": Content moves from bottom to top
            - "down": Content moves from top to bottom
        behavior: Animation behavior.
            - "scroll" (default): Continuous loop, content re-enters seamlessly
            - "alternate": Bounces back and forth between edges
            - "slide": Scrolls once and stops at the end
        pause_on_hover: Pause animation when mouse hovers over marquee. Default: True.
        gap: Gap in pixels between repeated content for seamless looping. Default: 50.
        clickable: Whether clicking the marquee emits an event. Default: False.
        separator: Optional separator string between repeated content (e.g., " • ").
        children: Nested toolbar items to scroll (alternative to text for complex content).

    Example:
        # Simple news ticker
        Marquee(
            text="Breaking News: Stock prices are up 5% today! • More updates coming soon...",
            event="ticker:click",
            speed=20,
            pause_on_hover=True,
        )

        # Bouncing alert
        Marquee(
            text="⚠️ System maintenance scheduled",
            behavior="alternate",
            speed=8,
            style="background: var(--pywry-accent); padding: 4px 8px;",
        )

        # Vertical scrolling credits
        Marquee(
            text="Thank you for using PyWry!",
            direction="up",
            speed=10,
        )

        # Complex nested content
        Marquee(
            children=[
                Button(label="🔔 Alert", event="alert:click", variant="ghost"),
                Div(content="<span>Important update available</span>"),
            ],
            speed=25,
            clickable=False,
        )

        # Dynamic ticker with Python updates
        ticker = Marquee(text="Loading...", speed=15, component_id="news-ticker")
        # Later: widget.emit("toolbar:marquee-set-content", {"id": "news-ticker", "text": "New content!"})
    """

    type: Literal["marquee"] = "marquee"
    text: str = ""
    speed: float = Field(
        default=15.0,
        ge=1.0,
        le=300.0,
        description="Duration in seconds for one scroll cycle (lower = faster)",
    )
    direction: Literal["left", "right", "up", "down"] = "left"
    behavior: Literal["scroll", "alternate", "slide"] = "scroll"
    pause_on_hover: bool = True
    gap: int = Field(
        default=50,
        ge=0,
        le=500,
        description="Gap in pixels between repeated content",
    )
    clickable: bool = False
    separator: str = Field(
        default="",
        description="Optional separator between repeated content (e.g., ' • ')",
    )
    # Forward reference to support nested toolbar items
    children: list[Any] | None = Field(
        default=None,
        description="Nested toolbar items to scroll (alternative to text)",
    )

    @model_validator(mode="after")
    def validate_content(self) -> Marquee:
        """Ensure either text or children is provided."""
        if not self.text and not self.children:
            # Allow empty marquee (will just be an empty scrolling container)
            pass
        return self

    def _build_children_html(self, parent_id: str | None = None) -> str:
        """Build HTML for nested children items.

        Parameters
        ----------
        parent_id : str | None
            Parent component ID for context chain.

        Returns
        -------
        str
            HTML string for all children.
        """
        if not self.children:
            return ""

        children_html = ""
        for child in self.children:
            if hasattr(child, "build_html"):
                # Pass context to Div children
                if isinstance(child, Div):
                    children_html += child.build_html(
                        parent_id=parent_id or self.component_id
                    )
                elif isinstance(child, Marquee):
                    # Nested marquees get parent context
                    children_html += child.build_html(
                        parent_id=parent_id or self.component_id
                    )
                else:
                    children_html += child.build_html()
        return children_html

    def _build_inner_content(self) -> str:
        """Build the inner content HTML (text or children).

        Returns
        -------
        str
            HTML string for inner content.
        """
        if self.children:
            return self._build_children_html(parent_id=self.component_id)
        # Use text content (allow simple HTML like <b>, <span>)
        if "<" in self.text and ">" in self.text:
            return self.text
        return html.escape(self.text)

    def _build_marquee_classes(self) -> list[str]:
        """Build CSS class list for the marquee element.

        Returns
        -------
        list[str]
            List of CSS class names.
        """
        classes = [
            "pywry-marquee",
            f"pywry-marquee-{self.direction}",
            f"pywry-marquee-{self.behavior}",
        ]
        # Axis class
        is_vertical = self.direction in ("up", "down")
        classes.append(
            "pywry-marquee-vertical" if is_vertical else "pywry-marquee-horizontal"
        )
        # Modifier classes
        if self.pause_on_hover:
            classes.append("pywry-marquee-pause")
        if self.clickable:
            classes.append("pywry-marquee-clickable")
        if self.disabled:
            classes.append("pywry-disabled")
        return classes

    def build_html(self, parent_id: str | None = None) -> str:
        """Build marquee HTML with CSS animation.

        Parameters
        ----------
        parent_id : str | None
            Parent component ID for context chain inheritance.

        Returns
        -------
        str
            HTML string for the marquee component.
        """
        classes = self._build_marquee_classes()

        # Build inline style with CSS custom properties
        style_parts = [
            f"--pywry-marquee-speed: {self.speed}s",
            f"--pywry-marquee-gap: {self.gap}px",
        ]
        if self.style:
            style_parts.append(self.style)

        # Build attributes
        attrs = [
            f'class="{" ".join(classes)}"',
            f'id="{self.component_id}"',
            f'data-component-id="{self.component_id}"',
            f'style="{"; ".join(style_parts)}"',
        ]
        if parent_id:
            attrs.append(f'data-parent-id="{parent_id}"')
        title_attr = self._build_title_attr()
        if title_attr:
            attrs.append(title_attr.strip())

        # Click handler attributes
        if self.clickable and not self.disabled:
            text_escaped = html.escape(self.text, quote=True) if self.text else ""
            attrs.append(f'data-text="{text_escaped}"')
            attrs.append(f'data-event="{self.event}"')

        # Build content and separator
        inner_content = self._build_inner_content()
        separator_html = ""
        if self.separator:
            separator_html = f'<span class="pywry-marquee-separator" aria-hidden="true">{html.escape(self.separator)}</span>'

        # For seamless continuous scroll, duplicate content
        marquee_html = (
            f"<div {' '.join(attrs)}>"
            f'<div class="pywry-marquee-track">'
            f'<span class="pywry-marquee-content">{inner_content}</span>'
            f"{separator_html}"
            f'<span class="pywry-marquee-content" aria-hidden="true">{inner_content}</span>'
            f"{separator_html}"
            f"</div>"
            f"</div>"
        )

        if not self.label:
            return marquee_html

        return (
            f'<div class="pywry-input-group pywry-input-inline">'
            f'<span class="pywry-input-label">{html.escape(self.label)}</span>'
            f"{marquee_html}"
            f"</div>"
        )

    def collect_scripts(self) -> list[str]:
        """Collect scripts from nested children (for consistency with Div).

        Returns
        -------
        list[str]
            List of script content strings from children.
        """
        scripts: list[str] = []
        if self.children:
            for child in self.children:
                if isinstance(child, (Div, Marquee)):
                    scripts.extend(child.collect_scripts())
        return scripts

    def update_payload(
        self,
        text: str | None = None,
        html_content: str | None = None,
        speed: float | None = None,
        paused: bool | None = None,
        separator: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Generate event name and payload for dynamic marquee updates.

        Use this with widget.emit() to update marquee content dynamically.

        Parameters
        ----------
        text : str | None
            New plain text content (will be escaped).
        html_content : str | None
            New HTML content (use instead of text for rich content).
        speed : float | None
            New animation speed in seconds.
        paused : bool | None
            True to pause, False to resume animation.
        separator : str | None
            New separator between repeated content.

        Returns
        -------
        tuple[str, dict[str, Any]]
            Event name and payload dict for widget.emit().

        Example
        -------
            ticker = Marquee(text="Loading...", component_id="news-ticker")
            # ... later ...
            event, data = ticker.update_payload(text="Breaking news!")
            widget.emit(event, data)

            # Or with speed change:
            event, data = ticker.update_payload(text="Urgent!", speed=8)
            widget.emit(event, data)
        """
        payload: dict[str, Any] = {"id": self.component_id}
        if text is not None:
            payload["text"] = text
        if html_content is not None:
            payload["html"] = html_content
        if speed is not None:
            payload["speed"] = speed
        if paused is not None:
            payload["paused"] = paused
        if separator is not None:
            payload["separator"] = separator
        return ("toolbar:marquee-set-content", payload)


# Type alias for any toolbar item (for type checkers)
ToolbarItemUnion = (
    Button
    | Select
    | MultiSelect
    | TextInput
    | TextArea
    | SecretInput
    | SearchInput
    | NumberInput
    | DateInput
    | SliderInput
    | RangeInput
    | Toggle
    | Checkbox
    | RadioGroup
    | TabGroup
    | Div
    | Marquee
)

# Annotated version with discriminator for Pydantic deserialization
AnyToolbarItem = Annotated[
    ToolbarItemUnion,
    Field(discriminator="type"),
]


# Rebuild models to resolve forward references for nested children
Div.model_rebuild()
Marquee.model_rebuild()


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
                Button(label="Refresh", event="app:refresh"),
                Select(label="View:", event="view:change", options=[...]),
                Div(content="<span>Custom</span>", class_name="custom-section"),
            ],
        )

        # Inside toolbar with custom positioning
        Toolbar(
            position="inside",
            style="bottom: 10px; right: 10px;",
            items=[Button(label="Action", event="app:action")],
        )
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    component_id: str = Field(default_factory=lambda: _generate_component_id("toolbar"))
    position: ToolbarPosition = "top"
    items: Sequence[ToolbarItemUnion] = Field(default_factory=list)
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
            resize_handle_html = f'<div class="pywry-resize-handle" data-toolbar-id="{self.component_id}"></div>'

        # For 'inside' position, style goes on outer div (for absolute positioning: top, right, etc.)
        # For other positions, style goes on content wrapper (for flex alignment)
        outer_style = ""
        content_style = ""
        if self.style:
            if self.position == "inside":
                outer_style = f' style="{self.style}"'
            else:
                content_style = f' style="{self.style}"'

        content_html = f'<div class="pywry-toolbar-content"{content_style}>{"".join(item_htmls)}</div>'

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
                script_path = (
                    Path(self.script) if isinstance(self.script, str) else self.script
                )
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
        """Convert toolbar to dict."""
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
                        exclude={
                            "component_id",
                            "type",
                            "label",
                            "event",
                            "style",
                            "disabled",
                        }
                    ),
                }
                for item in self.items
            ],
            "style": self.style,
            "class_name": self.class_name,
            "collapsible": self.collapsible,
            "resizable": self.resizable,
        }

    def get_secret_inputs(self) -> list[SecretInput]:
        """Get all SecretInput items in this toolbar (including nested in Divs).

        Returns
        -------
        list[SecretInput]
            All SecretInput components found.
        """
        secrets: list[SecretInput] = []

        def collect_from_items(items: Sequence[ToolbarItemUnion]) -> None:
            for item in items:
                if isinstance(item, SecretInput):
                    secrets.append(item)
                elif isinstance(item, Div) and item.children:
                    collect_from_items(item.children)

        collect_from_items(self.items)
        return secrets

    def register_secrets(self) -> None:
        """Register all SecretInput values in the secret registry.

        Called automatically when rendering. Ensures secrets are available
        for reveal/copy handlers.
        """
        for secret_input in self.get_secret_inputs():
            secret_input.register()

    def get_secret_events(self) -> list[tuple[str, str, str]]:
        """Get all secret-related events that need handlers.

        Returns
        -------
        list[tuple[str, str, str]]
            List of (component_id, reveal_event, copy_event) tuples.
        """
        return [
            (
                si.component_id,
                si.get_reveal_event(),
                si.get_copy_event(),
            )
            for si in self.get_secret_inputs()
        ]


def create_default_secret_handlers(
    dispatch_func: Callable[[str, dict[str, Any]], None],
) -> dict[str, Callable[..., Callable[[dict[str, Any], str, str], None]]]:
    """Create default handlers for secret reveal/copy events.

    These handlers look up the secret from the registry and dispatch
    the response back to the frontend.

    Parameters
    ----------
    dispatch_func : Callable
        Function to dispatch events to frontend: dispatch(event_type, data)

    Returns
    -------
    dict[str, Callable[..., Callable[[dict[str, Any], str, str], None]]]
        Mapping of handler name to factory function.
        - "reveal": factory(event_base: str) -> handler
        - "copy": factory(event_base: str) -> handler
        - "update": factory(secret_input: SecretInput) -> handler

    Example
    -------
        handlers = create_default_secret_handlers(app.dispatch)
        for event, handler in handlers.items():
            app.on(event, handler)
    """

    def make_reveal_handler(
        event_base: str,
    ) -> Callable[[dict[str, Any], str, str], None]:
        """Create handler for secret reveal events."""

        #  pylint: disable=unused-argument
        def handler(data: dict[str, Any], event_type: str, label: str) -> None:
            component_id = data.get("componentId", "")
            reveal_event = f"{event_base}:reveal"
            custom = get_secret_handler(reveal_event)
            secret = custom(data) if custom else get_secret(component_id)
            # Encode for transit obfuscation and dispatch response
            encoded_value = encode_secret(secret) if secret else ""
            dispatch_func(
                f"{event_base}:reveal-response",
                {
                    "componentId": component_id,
                    "value": encoded_value,
                    "encoded": True,
                },
            )

        return handler

    def make_copy_handler(
        event_base: str,
    ) -> Callable[[dict[str, Any], str, str], None]:
        # pylint: disable=unused-argument
        def handler(
            data: dict[str, Any],
            event_type: str,
            label: str,
        ) -> None:
            component_id = data.get("componentId", "")
            # Check for custom handler first
            copy_event = f"{event_base}:copy"
            custom = get_secret_handler(copy_event)
            secret = custom(data) if custom else get_secret(component_id)
            # Encode for transit obfuscation and dispatch response
            encoded_value = encode_secret(secret) if secret else ""
            dispatch_func(
                f"{event_base}:copy-response",
                {
                    "componentId": component_id,
                    "value": encoded_value,
                    "encoded": True,
                },
            )

        return handler

    def make_update_handler(
        secret_input: SecretInput,
    ) -> Callable[[dict[str, Any], str, str], None]:
        """Create handler that updates the secret registry when user edits value."""

        # pylint: disable=unused-argument
        def handler(data: dict[str, Any], event_type: str, label: str) -> None:
            # Only handle if this is a value update from frontend
            if "value" not in data:
                return
            value = data.get("value", "")
            is_encoded = data.get("encoded", False)
            secret_input.update_secret(value, encoded=is_encoded)

        return handler

    # Return factory functions - actual handlers created per-event
    return {
        "reveal": make_reveal_handler,
        "copy": make_copy_handler,
        "update": make_update_handler,
    }


def register_secret_handlers_for_toolbar(
    toolbar: Toolbar,
    on_func: Callable[[str, Callable[..., Any]], Any],
    dispatch_func: Callable[[str, dict[str, Any]], None],
) -> list[str]:
    """Register default secret handlers for all SecretInputs in a toolbar.

    Parameters
    ----------
    toolbar : Toolbar
        The toolbar containing SecretInput items.
    on_func : Callable
        Function to register event handlers: on(event_type, handler) -> Any
        Returns value is truthy if registration succeeded (or ignored).
    dispatch_func : Callable
        Function to dispatch events to frontend: dispatch(event_type, data)

    Returns
    -------
    list[str]
        List of event types that were registered.
    """
    registered: list[str] = []
    factories = create_default_secret_handlers(dispatch_func)

    for si in toolbar.get_secret_inputs():
        # Register the secret value
        si.register()

        # Get the base event (without :reveal/:copy suffix)
        base_event = si.event

        # Register update handler for when user edits the value
        # This updates the secret registry so reveal/copy work with new values
        update_handler = factories["update"](si)
        on_func(base_event, update_handler)
        registered.append(base_event)

        # Register reveal handler
        reveal_event = si.get_reveal_event()
        reveal_handler = factories["reveal"](base_event)
        on_func(reveal_event, reveal_handler)
        registered.append(reveal_event)

        # Register copy handler
        copy_event = si.get_copy_event()
        copy_handler = factories["copy"](base_event)
        on_func(copy_event, copy_handler)
        registered.append(copy_event)

    return registered


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
    "marquee": Marquee,
}


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


@lru_cache(maxsize=1)
def _get_toolbar_handlers_js() -> str:
    """Load centralized toolbar handler JavaScript.

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
    - Dynamic toolbar updates via toolbar:set-value event

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
    # Toast container div - ALWAYS included for alert support
    toast_container = "<div class='pywry-toast-container pywry-toast-container--top-right' aria-label='Notifications'></div>"

    if not toolbars and not extra_top_html:
        # No toolbars - just wrap in pywry-content with inner scroll container + toast container
        return f"<div class='pywry-content'><div class='pywry-scroll-container'>{content}</div></div>{toast_container}"

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

    for toolbar_cfg in toolbars or []:
        # Extract position and html from toolbar config
        if isinstance(toolbar_cfg, Toolbar):
            pos, html_str = toolbar_cfg.position, toolbar_cfg.build_html()
        elif hasattr(toolbar_cfg, "build_html"):
            pos = getattr(toolbar_cfg, "position", "top")
            html_str = toolbar_cfg.build_html()
        else:
            pos = toolbar_cfg.get("position", "top")
            items = toolbar_cfg.get("items", [])
            html_str = Toolbar(position=pos, items=items).build_html() if items else ""

        if not html_str or pos not in toolbar_html:
            continue

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
    # content -> inside -> top/bottom -> body-scroll -> left/right -> header/footer
    # This makes LEFT/RIGHT extend full height between HEADER/FOOTER (outside scroll)
    # The body-scroll wrapper enables scrolling for top/bottom/content only

    # Wrap content in pywry-content with inner scroll container
    wrapped = f"<div class='pywry-content'><div class='pywry-scroll-container'>{content}</div></div>"

    # Inside toolbars (overlay) - positioned relative to wrapper, stay fixed during scroll
    if inside_str:
        wrapped = f"<div class='pywry-wrapper-inside'>{inside_str}{wrapped}</div>"

    # Top/Bottom (inside body-scroll, so they scroll with content)
    if top_str or bottom_str:
        wrapped = f"<div class='pywry-wrapper-top'>{top_str}{wrapped}{bottom_str}</div>"

    # Body scroll wrapper - enables scrolling for top/bottom/content area as a whole
    # Applied BEFORE left/right so sidebars extend full height and scroll independently
    # Uses custom scrollbar system via pywry-scroll-container class
    if header_str or footer_str:
        wrapped = (
            f"<div class='pywry-body-scroll pywry-scroll-container'>{wrapped}</div>"
        )

    # Left/Right (extend full height, OUTSIDE body-scroll)
    if left_str or right_str:
        wrapped = (
            f"<div class='pywry-wrapper-left'>{left_str}{wrapped}{right_str}</div>"
        )

    # Header/Footer (outermost, full width)
    if header_str or footer_str:
        wrapped = (
            f"<div class='pywry-wrapper-header'>{header_str}{wrapped}{footer_str}</div>"
        )

    # Add toast container (defined earlier, always included)
    wrapped = wrapped + toast_container

    return wrapped
