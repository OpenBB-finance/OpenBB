"""Unit tests for toolbar Pydantic models.

Tests cover:
- Option model
- Base ToolbarItem functionality
- Individual item types (Button, Select, MultiSelect, TextInput, NumberInput, DateInput, RangeInput)
- Toolbar container
- Event validation
- HTML generation
- Helper functions
"""

from __future__ import annotations

import pytest

from pydantic import ValidationError

from pywry.toolbar import (
    RESERVED_NAMESPACES,
    Button,
    DateInput,
    MultiSelect,
    NumberInput,
    Option,
    RangeInput,
    Select,
    TextInput,
    Toolbar,
    build_toolbar_html,
    build_toolbars_by_position,
    build_toolbars_html,
    validate_event_format,
)


# =============================================================================
# Event Validation Tests
# =============================================================================


class TestValidateEventFormat:
    """Test the validate_event_format function."""

    def test_valid_simple_event(self) -> None:
        """Test simple valid event."""
        assert validate_event_format("toolbar:click") is True

    def test_valid_with_hyphen(self) -> None:
        """Test event with hyphen."""
        assert validate_event_format("view:change-mode") is True

    def test_valid_with_underscore(self) -> None:
        """Test event with underscore."""
        assert validate_event_format("data:row_selected") is True

    def test_valid_mixed_case(self) -> None:
        """Test mixed case event."""
        assert validate_event_format("MyApp:updateView") is True

    def test_invalid_no_namespace(self) -> None:
        """Test event without namespace."""
        assert validate_event_format("click") is False

    def test_invalid_empty_namespace(self) -> None:
        """Test event with empty namespace."""
        assert validate_event_format(":click") is False

    def test_invalid_empty_event(self) -> None:
        """Test event with empty event name."""
        assert validate_event_format("toolbar:") is False

    def test_invalid_empty_string(self) -> None:
        """Test empty string."""
        assert validate_event_format("") is False

    def test_invalid_starts_with_number_namespace(self) -> None:
        """Test namespace starting with number."""
        assert validate_event_format("1toolbar:click") is False

    def test_invalid_starts_with_number_event(self) -> None:
        """Test event starting with number."""
        assert validate_event_format("toolbar:1click") is False

    def test_invalid_special_chars(self) -> None:
        """Test event with special characters."""
        assert validate_event_format("toolbar:click@event") is False

    def test_invalid_multiple_colons(self) -> None:
        """Test event with multiple colons."""
        assert validate_event_format("toolbar:sub:click") is False


class TestReservedNamespaces:
    """Test that reserved namespaces are blocked."""

    def test_pywry_namespace_blocked(self) -> None:
        """Test that pywry namespace is blocked."""
        with pytest.raises(ValidationError, match="Reserved namespace 'pywry'"):
            Button(label="Test", event="pywry:click")

    def test_plotly_namespace_blocked(self) -> None:
        """Test that plotly namespace is blocked."""
        with pytest.raises(ValidationError, match="Reserved namespace 'plotly'"):
            Button(label="Test", event="plotly:click")

    def test_grid_namespace_blocked(self) -> None:
        """Test that grid namespace is blocked."""
        with pytest.raises(ValidationError, match="Reserved namespace 'grid'"):
            Button(label="Test", event="grid:select")

    def test_reserved_namespaces_are_lowercase_checked(self) -> None:
        """Test that reserved namespace check is case-insensitive."""
        with pytest.raises(ValidationError, match="Reserved namespace"):
            Button(label="Test", event="PYWRY:click")

    def test_all_reserved_namespaces_exist(self) -> None:
        """Test expected reserved namespaces are defined."""
        assert "pywry" in RESERVED_NAMESPACES
        assert "plotly" in RESERVED_NAMESPACES
        assert "grid" in RESERVED_NAMESPACES


# =============================================================================
# Option Model Tests
# =============================================================================


class TestOption:
    """Test the Option model."""

    def test_creates_with_label_only(self) -> None:
        """Test creating option with label only."""
        opt = Option(label="Test")
        assert opt.label == "Test"
        assert opt.value == "Test"

    def test_creates_with_label_and_value(self) -> None:
        """Test creating option with both label and value."""
        opt = Option(label="Display", value="internal")
        assert opt.label == "Display"
        assert opt.value == "internal"

    def test_option_is_frozen(self) -> None:
        """Test that Option is immutable."""
        opt = Option(label="Test")
        with pytest.raises(ValidationError):
            opt.label = "Changed"

    def test_value_defaults_to_label(self) -> None:
        """Test value defaults to label when not provided."""
        opt = Option(label="MyLabel")
        assert opt.value == "MyLabel"


# =============================================================================
# ToolbarItem Base Tests
# =============================================================================


class TestToolbarItemEventValidation:
    """Test event validation on ToolbarItem subclasses."""

    def test_valid_event_accepted(self) -> None:
        """Test valid event is accepted."""
        btn = Button(label="Test", event="toolbar:click")
        assert btn.event == "toolbar:click"

    def test_empty_event_rejected(self) -> None:
        """Test empty event is rejected."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            Button(label="Test", event="")

    def test_whitespace_event_rejected(self) -> None:
        """Test whitespace-only event is rejected."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            Button(label="Test", event="   ")

    def test_invalid_format_rejected(self) -> None:
        """Test invalid format is rejected."""
        with pytest.raises(ValidationError, match="Invalid event format"):
            Button(label="Test", event="click")

    def test_event_trimmed(self) -> None:
        """Test event whitespace is trimmed."""
        btn = Button(label="Test", event="  toolbar:click  ")
        assert btn.event == "toolbar:click"


class TestToolbarItemComponentId:
    """Test component ID generation."""

    def test_auto_generates_component_id(self) -> None:
        """Test component ID is auto-generated."""
        btn = Button(label="Test", event="toolbar:click")
        assert btn.component_id.startswith("item-")
        assert len(btn.component_id) == len("item-") + 8

    def test_custom_component_id(self) -> None:
        """Test custom component ID is preserved."""
        btn = Button(label="Test", event="toolbar:click", component_id="my-button")
        assert btn.component_id == "my-button"

    def test_unique_component_ids(self) -> None:
        """Test each item gets unique component ID."""
        btn1 = Button(label="One", event="toolbar:click")
        btn2 = Button(label="Two", event="toolbar:click")
        assert btn1.component_id != btn2.component_id


class TestToolbarItemDescription:
    """Test description/tooltip functionality."""

    def test_default_description_empty(self) -> None:
        """Test description defaults to empty string."""
        btn = Button(label="Test", event="toolbar:click")
        assert btn.description == ""

    def test_description_set(self) -> None:
        """Test description can be set."""
        btn = Button(label="Test", event="toolbar:click", description="Click me")
        assert btn.description == "Click me"

    def test_description_in_html_title(self) -> None:
        """Test description becomes title attribute."""
        btn = Button(label="Test", event="toolbar:click", description="Tooltip text")
        html = btn.build_html()
        assert 'title="Tooltip text"' in html

    def test_no_title_when_no_description(self) -> None:
        """Test no title attribute when description is empty."""
        btn = Button(label="Test", event="toolbar:click")
        html = btn.build_html()
        assert "title=" not in html


class TestToolbarItemDisabled:
    """Test disabled state."""

    def test_default_not_disabled(self) -> None:
        """Test items are not disabled by default."""
        btn = Button(label="Test", event="toolbar:click")
        assert btn.disabled is False

    def test_disabled_attribute_in_html(self) -> None:
        """Test disabled attribute appears in HTML."""
        btn = Button(label="Test", event="toolbar:click", disabled=True)
        html = btn.build_html()
        assert " disabled" in html


# =============================================================================
# Button Tests
# =============================================================================


class TestButton:
    """Test the Button model."""

    def test_type_is_button(self) -> None:
        """Test type field is 'button'."""
        btn = Button(label="Test", event="toolbar:click")
        assert btn.type == "button"

    def test_default_data_empty_dict(self) -> None:
        """Test data defaults to empty dict."""
        btn = Button(label="Test", event="toolbar:click")
        assert btn.data == {}

    def test_data_payload(self) -> None:
        """Test custom data payload."""
        btn = Button(label="Test", event="toolbar:click", data={"key": "value"})
        assert btn.data == {"key": "value"}

    def test_html_contains_button_tag(self) -> None:
        """Test HTML contains button element."""
        btn = Button(label="Click Me", event="toolbar:click")
        html = btn.build_html()
        assert "<button" in html
        assert "</button>" in html

    def test_html_contains_label(self) -> None:
        """Test HTML contains button label."""
        btn = Button(label="Click Me", event="toolbar:click")
        html = btn.build_html()
        assert "Click Me" in html

    def test_html_contains_pywry_emit(self) -> None:
        """Test HTML contains pywry.emit call."""
        btn = Button(label="Test", event="toolbar:click")
        html = btn.build_html()
        assert "window.pywry.emit" in html
        assert "toolbar:click" in html

    def test_html_contains_data_attribute(self) -> None:
        """Test HTML contains data-event-data attribute."""
        btn = Button(label="Test", event="toolbar:click", data={"test": 123})
        html = btn.build_html()
        assert "data-event-data" in html

    def test_html_class_pywry_btn(self) -> None:
        """Test HTML has pywry-btn class."""
        btn = Button(label="Test", event="toolbar:click")
        html = btn.build_html()
        assert 'class="pywry-btn"' in html

    def test_html_escapes_label(self) -> None:
        """Test HTML escapes special characters in label."""
        btn = Button(label="<script>alert('xss')</script>", event="toolbar:click")
        html = btn.build_html()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


# =============================================================================
# Select Tests
# =============================================================================


class TestSelect:
    """Test the Select model."""

    def test_type_is_select(self) -> None:
        """Test type field is 'select'."""
        sel = Select(event="view:change", options=[Option(label="A")])
        assert sel.type == "select"

    def test_options_from_option_objects(self) -> None:
        """Test options from Option objects."""
        sel = Select(
            event="view:change",
            options=[Option(label="One", value="1"), Option(label="Two", value="2")],
        )
        assert len(sel.options) == 2
        assert sel.options[0].label == "One"

    def test_options_from_dicts(self) -> None:
        """Test options from dict input."""
        sel = Select(
            event="view:change",
            options=[{"label": "One", "value": "1"}, {"label": "Two", "value": "2"}],
        )
        assert len(sel.options) == 2
        assert sel.options[0].value == "1"

    def test_options_from_strings(self) -> None:
        """Test options from string input."""
        sel = Select(event="view:change", options=["A", "B", "C"])
        assert len(sel.options) == 3
        assert sel.options[0].label == "A"
        assert sel.options[0].value == "A"

    def test_selected_value(self) -> None:
        """Test selected value."""
        sel = Select(
            event="view:change",
            options=[Option(label="A"), Option(label="B")],
            selected="B",
        )
        assert sel.selected == "B"

    def test_html_contains_select_tag(self) -> None:
        """Test HTML contains select element."""
        sel = Select(event="view:change", options=[Option(label="A")])
        html = sel.build_html()
        assert "<select" in html
        assert "</select>" in html

    def test_html_contains_options(self) -> None:
        """Test HTML contains option elements."""
        sel = Select(event="view:change", options=[Option(label="Opt1"), Option(label="Opt2")])
        html = sel.build_html()
        assert "<option" in html
        assert "Opt1" in html
        assert "Opt2" in html

    def test_html_marks_selected_option(self) -> None:
        """Test HTML marks selected option."""
        sel = Select(
            event="view:change",
            options=[Option(label="A"), Option(label="B")],
            selected="B",
        )
        html = sel.build_html()
        assert 'value="B" selected' in html

    def test_html_with_label(self) -> None:
        """Test HTML includes label wrapper."""
        sel = Select(label="Choose:", event="view:change", options=[Option(label="A")])
        html = sel.build_html()
        assert "Choose:" in html
        assert "pywry-input-label" in html

    def test_html_class_pywry_select(self) -> None:
        """Test HTML has pywry-select class."""
        sel = Select(event="view:change", options=[Option(label="A")])
        html = sel.build_html()
        assert 'class="pywry-select"' in html


# =============================================================================
# MultiSelect Tests
# =============================================================================


class TestMultiSelect:
    """Test the MultiSelect model."""

    def test_type_is_multiselect(self) -> None:
        """Test type field is 'multiselect'."""
        ms = MultiSelect(event="filter:columns", options=[Option(label="A")])
        assert ms.type == "multiselect"

    def test_selected_as_list(self) -> None:
        """Test selected is a list."""
        ms = MultiSelect(
            event="filter:columns",
            options=[Option(label="A"), Option(label="B")],
            selected=["A", "B"],
        )
        assert ms.selected == ["A", "B"]

    def test_selected_single_string_converted(self) -> None:
        """Test single string converted to list."""
        ms = MultiSelect(
            event="filter:columns",
            options=[Option(label="A")],
            selected="A",
        )
        assert ms.selected == ["A"]

    def test_html_contains_checkboxes(self) -> None:
        """Test HTML contains checkbox inputs."""
        ms = MultiSelect(
            event="filter:columns",
            options=[Option(label="A"), Option(label="B")],
        )
        html = ms.build_html()
        assert 'type="checkbox"' in html

    def test_html_marks_checked_options(self) -> None:
        """Test HTML marks checked options."""
        ms = MultiSelect(
            event="filter:columns",
            options=[Option(label="A"), Option(label="B")],
            selected=["A"],
        )
        html = ms.build_html()
        assert "checked" in html

    def test_html_class_pywry_multiselect(self) -> None:
        """Test HTML has pywry-multiselect class."""
        ms = MultiSelect(event="filter:columns", options=[Option(label="A")])
        html = ms.build_html()
        assert 'class="pywry-multiselect"' in html


# =============================================================================
# TextInput Tests
# =============================================================================


class TestTextInput:
    """Test the TextInput model."""

    def test_type_is_text(self) -> None:
        """Test type field is 'text'."""
        ti = TextInput(event="search:query")
        assert ti.type == "text"

    def test_default_debounce(self) -> None:
        """Test default debounce is 300ms."""
        ti = TextInput(event="search:query")
        assert ti.debounce == 300

    def test_custom_debounce(self) -> None:
        """Test custom debounce value."""
        ti = TextInput(event="search:query", debounce=500)
        assert ti.debounce == 500

    def test_debounce_minimum(self) -> None:
        """Test debounce cannot be negative."""
        with pytest.raises(ValidationError):
            TextInput(event="search:query", debounce=-1)

    def test_placeholder(self) -> None:
        """Test placeholder attribute."""
        ti = TextInput(event="search:query", placeholder="Type here...")
        assert ti.placeholder == "Type here..."

    def test_html_contains_text_input(self) -> None:
        """Test HTML contains text input."""
        ti = TextInput(event="search:query")
        html = ti.build_html()
        assert 'type="text"' in html

    def test_html_contains_placeholder(self) -> None:
        """Test HTML contains placeholder."""
        ti = TextInput(event="search:query", placeholder="Search...")
        html = ti.build_html()
        assert 'placeholder="Search..."' in html

    def test_html_contains_debounce(self) -> None:
        """Test HTML contains debounce timeout."""
        ti = TextInput(event="search:query", debounce=500)
        html = ti.build_html()
        assert "500" in html
        assert "setTimeout" in html


# =============================================================================
# NumberInput Tests
# =============================================================================


class TestNumberInput:
    """Test the NumberInput model."""

    def test_type_is_number(self) -> None:
        """Test type field is 'number'."""
        ni = NumberInput(event="limit:set")
        assert ni.type == "number"

    def test_value_optional(self) -> None:
        """Test value is optional."""
        ni = NumberInput(event="limit:set")
        assert ni.value is None

    def test_min_max_step(self) -> None:
        """Test min, max, step constraints."""
        ni = NumberInput(event="limit:set", min=0, max=100, step=5)
        assert ni.min == 0
        assert ni.max == 100
        assert ni.step == 5

    def test_html_contains_number_input(self) -> None:
        """Test HTML contains number input."""
        ni = NumberInput(event="limit:set")
        html = ni.build_html()
        assert 'type="number"' in html

    def test_html_contains_min_max(self) -> None:
        """Test HTML contains min/max attributes."""
        ni = NumberInput(event="limit:set", min=1, max=10)
        html = ni.build_html()
        assert 'min="1"' in html
        assert 'max="10"' in html

    def test_html_excludes_none_attributes(self) -> None:
        """Test HTML excludes None attributes."""
        ni = NumberInput(event="limit:set")
        html = ni.build_html()
        assert "min=" not in html
        assert "max=" not in html


# =============================================================================
# DateInput Tests
# =============================================================================


class TestDateInput:
    """Test the DateInput model."""

    def test_type_is_date(self) -> None:
        """Test type field is 'date'."""
        di = DateInput(event="date:change")
        assert di.type == "date"

    def test_value_format(self) -> None:
        """Test date value."""
        di = DateInput(event="date:change", value="2025-01-10")
        assert di.value == "2025-01-10"

    def test_min_max_dates(self) -> None:
        """Test min/max date constraints."""
        di = DateInput(event="date:change", min="2020-01-01", max="2030-12-31")
        assert di.min == "2020-01-01"
        assert di.max == "2030-12-31"

    def test_html_contains_date_input(self) -> None:
        """Test HTML contains date input."""
        di = DateInput(event="date:change")
        html = di.build_html()
        assert 'type="date"' in html

    def test_html_contains_value(self) -> None:
        """Test HTML contains value attribute."""
        di = DateInput(event="date:change", value="2025-01-10")
        html = di.build_html()
        assert 'value="2025-01-10"' in html


# =============================================================================
# RangeInput Tests
# =============================================================================


class TestRangeInput:
    """Test the RangeInput model."""

    def test_type_is_range(self) -> None:
        """Test type field is 'range'."""
        ri = RangeInput(event="zoom:level")
        assert ri.type == "range"

    def test_default_values(self) -> None:
        """Test default values."""
        ri = RangeInput(event="zoom:level")
        assert ri.value == 50
        assert ri.min == 0
        assert ri.max == 100
        assert ri.step == 1
        assert ri.show_value is True

    def test_custom_range(self) -> None:
        """Test custom range values."""
        ri = RangeInput(event="zoom:level", value=25, min=10, max=50, step=5)
        assert ri.value == 25
        assert ri.min == 10
        assert ri.max == 50
        assert ri.step == 5

    def test_html_contains_range_input(self) -> None:
        """Test HTML contains range input."""
        ri = RangeInput(event="zoom:level")
        html = ri.build_html()
        assert 'type="range"' in html

    def test_html_shows_value_display(self) -> None:
        """Test HTML shows value display span."""
        ri = RangeInput(event="zoom:level", value=75, show_value=True)
        html = ri.build_html()
        assert 'class="pywry-range-value"' in html
        assert ">75<" in html

    def test_html_hides_value_display(self) -> None:
        """Test HTML hides value when show_value=False."""
        ri = RangeInput(event="zoom:level", show_value=False)
        html = ri.build_html()
        assert "pywry-range-value" not in html


# =============================================================================
# Toolbar Container Tests
# =============================================================================


class TestToolbar:
    """Test the Toolbar container model."""

    def test_default_position_top(self) -> None:
        """Test default position is 'top'."""
        tb = Toolbar(items=[Button(label="Test", event="toolbar:click")])
        assert tb.position == "top"

    def test_all_positions_valid(self) -> None:
        """Test all positions are valid."""
        for pos in ["top", "bottom", "left", "right", "inside"]:
            tb = Toolbar(position=pos, items=[])
            assert tb.position == pos

    def test_invalid_position_rejected(self) -> None:
        """Test invalid position is rejected."""
        with pytest.raises(ValidationError):
            Toolbar(position="center", items=[])

    def test_auto_generates_component_id(self) -> None:
        """Test component ID is auto-generated."""
        tb = Toolbar(items=[])
        assert tb.component_id.startswith("toolbar-")

    def test_custom_component_id(self) -> None:
        """Test custom component ID."""
        tb = Toolbar(component_id="my-toolbar", items=[])
        assert tb.component_id == "my-toolbar"

    def test_items_from_models(self) -> None:
        """Test items from model objects."""
        tb = Toolbar(
            items=[
                Button(label="Btn", event="toolbar:click"),
                Select(event="view:change", options=[Option(label="A")]),
            ]
        )
        assert len(tb.items) == 2
        assert isinstance(tb.items[0], Button)
        assert isinstance(tb.items[1], Select)

    def test_items_from_dicts(self) -> None:
        """Test items from dict input."""
        tb = Toolbar(
            items=[
                {"type": "button", "label": "Btn", "event": "toolbar:click"},
                {"type": "select", "event": "view:change", "options": ["A", "B"]},
            ]
        )
        assert len(tb.items) == 2
        assert isinstance(tb.items[0], Button)
        assert isinstance(tb.items[1], Select)

    def test_items_unknown_type_rejected(self) -> None:
        """Test unknown item type is rejected."""
        with pytest.raises(ValueError, match="Unknown toolbar item type"):
            Toolbar(items=[{"type": "unknown", "event": "test:event"}])

    def test_empty_toolbar_builds_empty_html(self) -> None:
        """Test empty toolbar builds empty HTML."""
        tb = Toolbar(items=[])
        assert tb.build_html() == ""

    def test_html_contains_toolbar_class(self) -> None:
        """Test HTML contains toolbar class."""
        tb = Toolbar(items=[Button(label="Test", event="toolbar:click")])
        html = tb.build_html()
        assert "pywry-toolbar" in html

    def test_html_contains_position_class(self) -> None:
        """Test HTML contains position class."""
        tb = Toolbar(position="bottom", items=[Button(label="Test", event="toolbar:click")])
        html = tb.build_html()
        assert "pywry-toolbar-bottom" in html

    def test_html_contains_all_items(self) -> None:
        """Test HTML contains all items."""
        tb = Toolbar(
            items=[
                Button(label="Btn1", event="toolbar:click1"),
                Button(label="Btn2", event="toolbar:click2"),
            ]
        )
        html = tb.build_html()
        assert "Btn1" in html
        assert "Btn2" in html

    def test_to_dict_method(self) -> None:
        """Test to_dict method."""
        tb = Toolbar(
            position="left",
            items=[Button(label="Test", event="toolbar:click", data={"key": "val"})],
        )
        d = tb.to_dict()
        assert d["position"] == "left"
        assert len(d["items"]) == 1
        assert d["items"][0]["label"] == "Test"

    def test_style_attribute(self) -> None:
        """Test style attribute in HTML."""
        tb = Toolbar(
            style="background: red;",
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = tb.build_html()
        assert 'style="background: red;"' in html


class TestToolbarExtraFieldsRejected:
    """Test that extra fields are rejected (typo protection)."""

    def test_button_extra_field_rejected(self) -> None:
        """Test Button rejects extra fields."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            Button(label="Test", event="toolbar:click", lable="typo")

    def test_select_extra_field_rejected(self) -> None:
        """Test Select rejects extra fields."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            Select(event="view:change", options=[], optins="typo")

    def test_toolbar_extra_field_rejected(self) -> None:
        """Test Toolbar rejects extra fields."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            Toolbar(items=[], positon="typo")


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestBuildToolbarHtml:
    """Test build_toolbar_html function."""

    def test_accepts_toolbar_model(self) -> None:
        """Test accepts Toolbar model."""
        tb = Toolbar(items=[Button(label="Test", event="toolbar:click")])
        html = build_toolbar_html(tb)
        assert "Test" in html

    def test_accepts_dict(self) -> None:
        """Test accepts dict input."""
        d = {
            "position": "top",
            "items": [{"type": "button", "label": "Test", "event": "toolbar:click"}],
        }
        html = build_toolbar_html(d)
        assert "Test" in html

    def test_empty_toolbar_returns_empty(self) -> None:
        """Test empty toolbar returns empty string."""
        html = build_toolbar_html(Toolbar(items=[]))
        assert html == ""


class TestBuildToolbarsHtml:
    """Test build_toolbars_html function."""

    def test_none_returns_empty(self) -> None:
        """Test None returns empty string."""
        html = build_toolbars_html(None)
        assert html == ""

    def test_empty_list_returns_empty(self) -> None:
        """Test empty list returns empty string."""
        html = build_toolbars_html([])
        assert html == ""

    def test_combines_multiple_toolbars(self) -> None:
        """Test combines multiple toolbars."""
        toolbars = [
            Toolbar(items=[Button(label="One", event="toolbar:one")]),
            Toolbar(items=[Button(label="Two", event="toolbar:two")]),
        ]
        html = build_toolbars_html(toolbars)
        assert "One" in html
        assert "Two" in html


class TestBuildToolbarsByPosition:
    """Test build_toolbars_by_position function."""

    def test_none_returns_empty_positions(self) -> None:
        """Test None returns empty positions."""
        result = build_toolbars_by_position(None)
        assert result["top"] == ""
        assert result["bottom"] == ""
        assert result["left"] == ""
        assert result["right"] == ""
        assert result["inside"] == ""

    def test_groups_by_position(self) -> None:
        """Test toolbars are grouped by position."""
        toolbars = [
            Toolbar(position="top", items=[Button(label="Top", event="toolbar:top")]),
            Toolbar(position="bottom", items=[Button(label="Bottom", event="toolbar:bottom")]),
            Toolbar(position="left", items=[Button(label="Left", event="toolbar:left")]),
        ]
        result = build_toolbars_by_position(toolbars)
        assert "Top" in result["top"]
        assert "Bottom" in result["bottom"]
        assert "Left" in result["left"]
        assert result["right"] == ""
        assert result["inside"] == ""

    def test_combines_same_position(self) -> None:
        """Test multiple toolbars at same position are combined."""
        toolbars = [
            Toolbar(position="top", items=[Button(label="One", event="toolbar:one")]),
            Toolbar(position="top", items=[Button(label="Two", event="toolbar:two")]),
        ]
        result = build_toolbars_by_position(toolbars)
        assert "One" in result["top"]
        assert "Two" in result["top"]

    def test_accepts_mixed_models_and_dicts(self) -> None:
        """Test accepts mix of Toolbar models and dicts."""
        toolbars = [
            Toolbar(position="top", items=[Button(label="Model", event="toolbar:model")]),
            {
                "position": "bottom",
                "items": [{"type": "button", "label": "Dict", "event": "toolbar:dict"}],
            },
        ]
        result = build_toolbars_by_position(toolbars)
        assert "Model" in result["top"]
        assert "Dict" in result["bottom"]


# =============================================================================
# Type Discriminator Tests
# =============================================================================


class TestAnyToolbarItemDiscriminator:
    """Test that type discriminator works correctly."""

    def test_button_discriminated(self) -> None:
        """Test Button is correctly identified by type."""
        btn = Button(label="Test", event="toolbar:click")
        assert btn.type == "button"

    def test_select_discriminated(self) -> None:
        """Test Select is correctly identified by type."""
        sel = Select(event="view:change", options=[])
        assert sel.type == "select"

    def test_all_types_have_unique_type_field(self) -> None:
        """Test all item types have unique type field values."""
        types = set()
        for cls in [Button, Select, MultiSelect, TextInput, NumberInput, DateInput, RangeInput]:
            # Create instance with minimal required fields
            if cls == Button:
                inst = cls(label="Test", event="toolbar:click")
            elif cls in (Select, MultiSelect):
                inst = cls(event="toolbar:click", options=[])
            else:
                inst = cls(event="toolbar:click")
            assert inst.type not in types, f"Duplicate type: {inst.type}"
            types.add(inst.type)


# =============================================================================
# HTML Security Tests
# =============================================================================


class TestHtmlSecurity:
    """Test HTML escaping and security."""

    def test_button_label_escaped(self) -> None:
        """Test button label is HTML escaped."""
        btn = Button(label='<img src=x onerror="alert(1)">', event="toolbar:click")
        html = btn.build_html()
        assert "<img" not in html
        assert "&lt;img" in html

    def test_select_label_escaped(self) -> None:
        """Test select label is HTML escaped."""
        sel = Select(label="<script>bad</script>", event="view:change", options=[])
        html = sel.build_html()
        assert "<script>" not in html

    def test_option_label_escaped(self) -> None:
        """Test option label is HTML escaped."""
        sel = Select(event="view:change", options=[Option(label="<b>bold</b>")])
        html = sel.build_html()
        assert "<b>" not in html

    def test_description_escaped(self) -> None:
        """Test description tooltip is HTML escaped."""
        btn = Button(label="Test", event="toolbar:click", description='">onclick="alert(1)')
        html = btn.build_html()
        # The malicious onclick in description should be escaped to &quot;
        # Check that the title attribute contains the escaped version
        assert 'title="&quot;&gt;onclick=&quot;alert(1)"' in html
        # The raw injection attempt should not appear unescaped
        assert '">onclick="alert(1)"' not in html


# =============================================================================
# Style Attribute Tests
# =============================================================================


class TestStyleAttribute:
    """Test style attribute handling."""

    def test_button_style(self) -> None:
        """Test button style attribute."""
        btn = Button(label="Test", event="toolbar:click", style="color: red;")
        html = btn.build_html()
        assert 'style="color: red;"' in html

    def test_select_with_label_style(self) -> None:
        """Test select style on wrapper."""
        sel = Select(label="Choose:", event="view:change", options=[], style="margin: 10px;")
        html = sel.build_html()
        assert "margin: 10px;" in html

    def test_toolbar_style(self) -> None:
        """Test toolbar container style."""
        tb = Toolbar(style="padding: 5px;", items=[Button(label="Test", event="toolbar:click")])
        html = tb.build_html()
        assert 'style="padding: 5px;"' in html
