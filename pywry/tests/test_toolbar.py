"""Unit tests for toolbar Pydantic models.

Tests cover:
- Option model
- Base ToolbarItem functionality
- Individual item types (Button, Select, MultiSelect, TextInput, NumberInput, DateInput, SliderInput, RangeInput)
- Toolbar container
- Event validation
- HTML generation
- Helper functions
"""
# pylint: disable=too-many-lines

from __future__ import annotations

import pytest

from pydantic import ValidationError

from pywry.toolbar import (
    RESERVED_NAMESPACES,
    Button,
    Checkbox,
    DateInput,
    Div,
    MultiSelect,
    NumberInput,
    Option,
    RadioGroup,
    RangeInput,
    Select,
    SliderInput,
    TabGroup,
    TextInput,
    Toggle,
    Toolbar,
    build_toolbar_html,
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

    def test_auto_generates_component_id_with_type(self) -> None:
        """Test component ID is auto-generated with component type prefix."""
        btn = Button(label="Test", event="toolbar:click")
        assert btn.component_id.startswith("button-")
        assert len(btn.component_id) == len("button-") + 8

    def test_select_component_id_has_select_prefix(self) -> None:
        """Test Select component ID uses 'select-' prefix."""
        sel = Select(event="view:change", options=["A"])
        assert sel.component_id.startswith("select-")

    def test_multiselect_component_id_has_multiselect_prefix(self) -> None:
        """Test MultiSelect component ID uses 'multiselect-' prefix."""
        ms = MultiSelect(event="filter:cols", options=["A"])
        assert ms.component_id.startswith("multiselect-")

    def test_text_input_component_id_has_text_prefix(self) -> None:
        """Test TextInput component ID uses 'text-' prefix."""
        ti = TextInput(event="search:query")
        assert ti.component_id.startswith("text-")

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

    def test_html_contains_data_event(self) -> None:
        """Test HTML contains data-event attribute for external handler."""
        btn = Button(label="Test", event="toolbar:click")
        html = btn.build_html()
        # Button now uses data-event attributes, handled by toolbar-handlers.js
        assert 'data-event="toolbar:click"' in html

    def test_html_contains_data_attribute(self) -> None:
        """Test HTML contains data-data attribute for event payload."""
        btn = Button(label="Test", event="toolbar:click", data={"test": 123})
        html = btn.build_html()
        # Data attribute is now called data-data
        assert "data-data" in html

    def test_html_class_pywry_btn(self) -> None:
        """Test HTML has pywry-btn class."""
        btn = Button(label="Test", event="toolbar:click")
        html = btn.build_html()
        # Button now has both pywry-btn and pywry-toolbar-button classes
        assert "pywry-btn" in html
        assert "pywry-toolbar-button" in html

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
        """Test HTML contains dropdown element (custom styled select)."""
        sel = Select(event="view:change", options=[Option(label="A")])
        html = sel.build_html()
        assert 'class="pywry-dropdown"' in html
        assert "pywry-dropdown-menu" in html

    def test_html_contains_options(self) -> None:
        """Test HTML contains option elements."""
        sel = Select(event="view:change", options=[Option(label="Opt1"), Option(label="Opt2")])
        html = sel.build_html()
        assert "pywry-dropdown-option" in html
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
        assert 'data-value="B"' in html
        assert "pywry-selected" in html

    def test_html_with_label(self) -> None:
        """Test HTML includes label wrapper."""
        sel = Select(label="Choose:", event="view:change", options=[Option(label="A")])
        html = sel.build_html()
        assert "Choose:" in html
        assert "pywry-input-label" in html

    def test_html_class_pywry_select(self) -> None:
        """Test HTML has pywry-dropdown class (styled select)."""
        sel = Select(event="view:change", options=[Option(label="A")])
        html = sel.build_html()
        assert 'class="pywry-dropdown"' in html


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
        # MultiSelect uses dropdown with pywry-multiselect class
        assert "pywry-multiselect" in html
        assert "pywry-dropdown" in html


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
# SliderInput Tests (single-value slider, formerly RangeInput)
# =============================================================================


class TestSliderInput:
    """Test the SliderInput model (single-value slider)."""

    def test_type_is_slider(self) -> None:
        """Test type field is 'slider'."""
        si = SliderInput(event="zoom:level")
        assert si.type == "slider"

    def test_default_values(self) -> None:
        """Test default values."""
        si = SliderInput(event="zoom:level")
        assert si.value == 50
        assert si.min == 0
        assert si.max == 100
        assert si.step == 1
        assert si.show_value is True

    def test_custom_range(self) -> None:
        """Test custom slider values."""
        si = SliderInput(event="zoom:level", value=25, min=10, max=50, step=5)
        assert si.value == 25
        assert si.min == 10
        assert si.max == 50
        assert si.step == 5

    def test_html_contains_range_input(self) -> None:
        """Test HTML contains range input element."""
        si = SliderInput(event="zoom:level")
        html = si.build_html()
        assert 'type="range"' in html

    def test_html_shows_value_display(self) -> None:
        """Test HTML shows value display span."""
        si = SliderInput(event="zoom:level", value=75, show_value=True)
        html = si.build_html()
        assert 'class="pywry-range-value"' in html
        assert ">75<" in html

    def test_html_hides_value_display(self) -> None:
        """Test HTML hides value when show_value=False."""
        si = SliderInput(event="zoom:level", show_value=False)
        html = si.build_html()
        assert "pywry-range-value" not in html


# =============================================================================
# RangeInput Tests (dual-handle range selector)
# =============================================================================


class TestRangeInput:
    """Test the RangeInput model (dual-handle range selector)."""

    def test_type_is_range(self) -> None:
        """Test type field is 'range'."""
        ri = RangeInput(event="zoom:level")
        assert ri.type == "range"

    def test_default_values(self) -> None:
        """Test default values."""
        ri = RangeInput(event="zoom:level")
        assert ri.start == 0
        assert ri.end == 100
        assert ri.min == 0
        assert ri.max == 100
        assert ri.step == 1
        assert ri.show_value is True

    def test_custom_range(self) -> None:
        """Test custom range values."""
        ri = RangeInput(event="filter:price", start=100, end=500, min=0, max=1000, step=10)
        assert ri.start == 100
        assert ri.end == 500
        assert ri.min == 0
        assert ri.max == 1000
        assert ri.step == 10

    def test_html_contains_two_range_inputs(self) -> None:
        """Test HTML contains two range input elements for start and end."""
        ri = RangeInput(event="zoom:level")
        html = ri.build_html()
        # Should have two range inputs
        assert html.count('type="range"') == 2
        # Should have the range group container
        assert 'class="pywry-range-group"' in html
        # Should have the track structure (not separator)
        assert 'class="pywry-range-track"' in html

    def test_html_shows_both_value_displays(self) -> None:
        """Test HTML shows value display spans for both sliders."""
        ri = RangeInput(event="zoom:level", start=25, end=75, show_value=True)
        html = ri.build_html()
        # Should have two value displays with position-specific classes
        assert "pywry-range-start-value" in html
        assert "pywry-range-end-value" in html
        assert ">25<" in html
        assert ">75<" in html

    def test_html_hides_value_display(self) -> None:
        """Test HTML hides value when show_value=False."""
        ri = RangeInput(event="zoom:level", show_value=False)
        html = ri.build_html()
        assert "pywry-range-value" not in html

    def test_html_contains_start_and_end_markers(self) -> None:
        """Test HTML contains proper markers for start and end sliders."""
        ri = RangeInput(event="zoom:level")
        html = ri.build_html()
        # Inputs now use data-range attribute instead of separate IDs
        assert 'data-range="start"' in html
        assert 'data-range="end"' in html


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
            Button(label="Test", event="toolbar:click", unknown_field="typo")

    def test_select_extra_field_rejected(self) -> None:
        """Test Select rejects extra fields."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            Select(event="view:change", options=[], unknown_field="typo")

    def test_toolbar_extra_field_rejected(self) -> None:
        """Test Toolbar rejects extra fields."""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            Toolbar(items=[], unknown_field="typo")


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
        for cls in [
            Button,
            Select,
            MultiSelect,
            TextInput,
            NumberInput,
            DateInput,
            SliderInput,
            RangeInput,
        ]:
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


# =============================================================================
# Div Container Tests
# =============================================================================


class TestDiv:
    """Test the Div container model."""

    def test_type_is_div(self) -> None:
        """Test type field is 'div'."""
        div = Div(event="toolbar:div")
        assert div.type == "div"

    def test_content_rendering(self) -> None:
        """Test content is rendered inside div."""
        div = Div(content="<h1>Hello</h1>", event="toolbar:div")
        html = div.build_html()
        assert "<h1>Hello</h1>" in html

    def test_html_class_pywry_div(self) -> None:
        """Test HTML has pywry-div class."""
        div = Div(event="toolbar:div")
        html = div.build_html()
        assert 'class="pywry-div"' in html

    def test_custom_class_name(self) -> None:
        """Test custom class_name is added."""
        div = Div(event="toolbar:div", class_name="my-custom-class")
        html = div.build_html()
        assert "pywry-div" in html
        assert "my-custom-class" in html

    def test_component_id_in_html(self) -> None:
        """Test component_id is in HTML attributes."""
        div = Div(event="toolbar:div", component_id="my-div")
        html = div.build_html()
        assert 'id="my-div"' in html
        assert 'data-component-id="my-div"' in html

    def test_parent_id_passed_to_html(self) -> None:
        """Test parent_id is added when provided."""
        div = Div(event="toolbar:div")
        html = div.build_html(parent_id="parent-toolbar")
        assert 'data-parent-id="parent-toolbar"' in html

    def test_no_parent_id_when_not_provided(self) -> None:
        """Test no data-parent-id when not provided."""
        div = Div(event="toolbar:div")
        html = div.build_html()
        assert "data-parent-id" not in html

    def test_nested_children(self) -> None:
        """Test nested toolbar items in children."""
        div = Div(
            content="<span>Header</span>",
            event="toolbar:div",
            children=[
                Button(label="Child Button", event="toolbar:child"),
            ],
        )
        html = div.build_html()
        assert "<span>Header</span>" in html
        assert "Child Button" in html

    def test_nested_divs(self) -> None:
        """Test nested Div elements."""
        parent = Div(
            content="<p>Parent</p>",
            event="toolbar:parent",
            component_id="parent-div",
            children=[
                Div(
                    content="<p>Child</p>",
                    event="toolbar:child",
                    component_id="child-div",
                ),
            ],
        )
        html = parent.build_html()
        assert "<p>Parent</p>" in html
        assert "<p>Child</p>" in html
        assert 'id="child-div"' in html

    def test_parent_context_inherited_by_nested_divs(self) -> None:
        """Test nested Divs get parent context."""
        parent = Div(
            content="",
            event="toolbar:parent",
            component_id="parent-div",
            children=[
                Div(
                    content="",
                    event="toolbar:child",
                    component_id="child-div",
                ),
            ],
        )
        html = parent.build_html(parent_id="toolbar-123")
        # Parent should have parent_id from build_html
        assert 'data-parent-id="toolbar-123"' in html
        # Child should have parent's component_id as its parent_id
        assert 'data-parent-id="parent-div"' in html

    def test_style_attribute(self) -> None:
        """Test style attribute in HTML."""
        div = Div(event="toolbar:div", style="background: red;")
        html = div.build_html()
        assert 'style="background: red;"' in html

    def test_script_inline(self) -> None:
        """Test inline script collection."""
        div = Div(event="toolbar:div", script="console.log('test');")
        scripts = div.collect_scripts()
        assert len(scripts) == 1
        assert "console.log('test');" in scripts[0]

    def test_collect_scripts_depth_first(self) -> None:
        """Test scripts collected depth-first (parent before children)."""
        parent = Div(
            event="toolbar:parent",
            script="// parent script",
            children=[
                Div(
                    event="toolbar:child",
                    script="// child script",
                ),
            ],
        )
        scripts = parent.collect_scripts()
        assert len(scripts) == 2
        assert "parent script" in scripts[0]
        assert "child script" in scripts[1]


class TestDivInToolbar:
    """Test Div integration within Toolbar."""

    def test_toolbar_with_div(self) -> None:
        """Test Toolbar containing Div."""
        toolbar = Toolbar(
            position="top",
            items=[
                Button(label="Before", event="toolbar:before"),
                Div(content="<span>Custom</span>", event="toolbar:div"),
                Button(label="After", event="toolbar:after"),
            ],
        )
        html = toolbar.build_html()
        assert "Before" in html
        assert "<span>Custom</span>" in html
        assert "After" in html
        assert "pywry-div" in html

    def test_toolbar_passes_parent_id_to_div(self) -> None:
        """Test Toolbar passes its component_id to Div children."""
        toolbar = Toolbar(
            component_id="my-toolbar",
            position="top",
            items=[
                Div(content="", event="toolbar:div", component_id="my-div"),
            ],
        )
        html = toolbar.build_html()
        assert 'data-parent-id="my-toolbar"' in html

    def test_toolbar_collect_scripts_includes_divs(self) -> None:
        """Test Toolbar.collect_scripts includes Div scripts."""
        toolbar = Toolbar(
            position="top",
            script="// toolbar script",
            items=[
                Div(event="toolbar:div", script="// div script"),
            ],
        )
        scripts = toolbar.collect_scripts()
        assert len(scripts) == 2
        assert "toolbar script" in scripts[0]
        assert "div script" in scripts[1]


# =============================================================================
# Toolbar New Parameters Tests
# =============================================================================


class TestToolbarClassname:
    """Test toolbar class_name parameter."""

    def test_class_name_in_html(self) -> None:
        """Test class_name is added to toolbar container."""
        toolbar = Toolbar(
            position="top",
            class_name="my-custom-toolbar",
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = toolbar.build_html()
        assert "pywry-toolbar" in html
        assert "my-custom-toolbar" in html

    def test_multiple_classes(self) -> None:
        """Test class_name combines with position class."""
        toolbar = Toolbar(
            position="left",
            class_name="custom-class",
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = toolbar.build_html()
        assert "pywry-toolbar" in html
        assert "pywry-toolbar-left" in html
        assert "custom-class" in html


class TestToolbarCollapsible:
    """Test toolbar collapsible parameter."""

    def test_collapsible_false_by_default(self) -> None:
        """Test collapsible is False by default."""
        toolbar = Toolbar(
            position="top",
            items=[Button(label="Test", event="toolbar:click")],
        )
        assert toolbar.collapsible is False

    def test_collapsible_data_attribute(self) -> None:
        """Test collapsible adds data attribute."""
        toolbar = Toolbar(
            position="top",
            collapsible=True,
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = toolbar.build_html()
        assert 'data-collapsible="true"' in html

    def test_collapsible_aria_expanded(self) -> None:
        """Test collapsible adds aria-expanded."""
        toolbar = Toolbar(
            position="top",
            collapsible=True,
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = toolbar.build_html()
        assert 'aria-expanded="true"' in html

    def test_collapsible_toggle_button(self) -> None:
        """Test collapsible adds toggle button."""
        toolbar = Toolbar(
            position="top",
            collapsible=True,
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = toolbar.build_html()
        assert "pywry-toolbar-toggle" in html
        assert "pywry-toggle-icon" in html

    def test_not_collapsible_no_toggle(self) -> None:
        """Test non-collapsible toolbar has no toggle."""
        toolbar = Toolbar(
            position="top",
            collapsible=False,
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = toolbar.build_html()
        assert "pywry-toolbar-toggle" not in html


class TestToolbarResizable:
    """Test toolbar resizable parameter."""

    def test_resizable_false_by_default(self) -> None:
        """Test resizable is False by default."""
        toolbar = Toolbar(
            position="top",
            items=[Button(label="Test", event="toolbar:click")],
        )
        assert toolbar.resizable is False

    def test_resizable_data_attribute(self) -> None:
        """Test resizable adds data attribute."""
        toolbar = Toolbar(
            position="top",
            resizable=True,
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = toolbar.build_html()
        assert 'data-resizable="true"' in html

    def test_resizable_resize_handle(self) -> None:
        """Test resizable adds resize handle."""
        toolbar = Toolbar(
            position="top",
            resizable=True,
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = toolbar.build_html()
        assert "pywry-resize-handle" in html

    def test_not_resizable_no_handle(self) -> None:
        """Test non-resizable toolbar has no resize handle."""
        toolbar = Toolbar(
            position="top",
            resizable=False,
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = toolbar.build_html()
        assert "pywry-resize-handle" not in html


class TestToolbarScript:
    """Test toolbar script parameter."""

    def test_script_none_by_default(self) -> None:
        """Test script is None by default."""
        toolbar = Toolbar(
            position="top",
            items=[Button(label="Test", event="toolbar:click")],
        )
        assert toolbar.script is None

    def test_collect_scripts_with_inline_script(self) -> None:
        """Test collect_scripts returns inline script."""
        toolbar = Toolbar(
            position="top",
            script="console.log('toolbar init');",
            items=[Button(label="Test", event="toolbar:click")],
        )
        scripts = toolbar.collect_scripts()
        assert len(scripts) == 1
        assert "console.log('toolbar init');" in scripts[0]

    def test_collect_scripts_empty_when_no_script(self) -> None:
        """Test collect_scripts returns empty list when no script."""
        toolbar = Toolbar(
            position="top",
            items=[Button(label="Test", event="toolbar:click")],
        )
        scripts = toolbar.collect_scripts()
        assert len(scripts) == 0


class TestToolbarDataAttributes:
    """Test toolbar data attributes in HTML."""

    def test_data_position_attribute(self) -> None:
        """Test data-position attribute is set."""
        for position in ["top", "bottom", "left", "right", "inside"]:
            toolbar = Toolbar(
                position=position,
                items=[Button(label="Test", event="toolbar:click")],
            )
            html = toolbar.build_html()
            assert f'data-position="{position}"' in html

    def test_data_component_id_attribute(self) -> None:
        """Test data-component-id attribute is set."""
        toolbar = Toolbar(
            component_id="test-toolbar",
            position="top",
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = toolbar.build_html()
        assert 'data-component-id="test-toolbar"' in html


class TestToolbarContentWrapper:
    """Test toolbar content wrapper element."""

    def test_content_wrapper_present(self) -> None:
        """Test pywry-toolbar-content wrapper is present."""
        toolbar = Toolbar(
            position="top",
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = toolbar.build_html()
        assert "pywry-toolbar-content" in html

    def test_items_inside_content_wrapper(self) -> None:
        """Test items are inside content wrapper."""
        toolbar = Toolbar(
            position="top",
            items=[Button(label="Test", event="toolbar:click")],
        )
        html = toolbar.build_html()
        # Content wrapper should contain the button
        assert '<div class="pywry-toolbar-content">' in html

    def test_style_on_content_wrapper_for_non_inside_positions(self) -> None:
        """Test style goes on content wrapper for top/bottom/left/right positions."""
        for position in ["top", "bottom", "left", "right"]:
            toolbar = Toolbar(
                position=position,  # type: ignore[arg-type]
                style="justify-content: center;",
                items=[Button(label="Test", event="toolbar:click")],
            )
            html = toolbar.build_html()
            # Style should be on the content wrapper
            assert 'class="pywry-toolbar-content" style="justify-content: center;"' in html
            # Outer div should NOT have style attribute
            assert f'class="pywry-toolbar pywry-toolbar-{position}"' in html
            assert f'pywry-toolbar-{position}" style=' not in html

    def test_style_on_outer_div_for_inside_position(self) -> None:
        """Test style goes on outer div for inside position (for absolute positioning)."""
        toolbar = Toolbar(
            position="inside",
            style="top: 40px; right: 20px;",
            items=[Button(label="Overlay", event="toolbar:click")],
        )
        html = toolbar.build_html()
        # Style should be on the outer div for inside position
        assert 'style="top: 40px; right: 20px;"' in html
        # Check style is NOT on content wrapper
        assert 'class="pywry-toolbar-content">' in html  # No style attr on content


class TestToolbarToDict:
    """Test toolbar to_dict includes new fields."""

    def test_to_dict_includes_class_name(self) -> None:
        """Test to_dict includes class_name."""
        toolbar = Toolbar(
            position="top",
            class_name="my-class",
            items=[Button(label="Test", event="toolbar:click")],
        )
        d = toolbar.to_dict()
        assert d["class_name"] == "my-class"

    def test_to_dict_includes_collapsible(self) -> None:
        """Test to_dict includes collapsible."""
        toolbar = Toolbar(
            position="top",
            collapsible=True,
            items=[Button(label="Test", event="toolbar:click")],
        )
        d = toolbar.to_dict()
        assert d["collapsible"] is True

    def test_to_dict_includes_resizable(self) -> None:
        """Test to_dict includes resizable."""
        toolbar = Toolbar(
            position="top",
            resizable=True,
            items=[Button(label="Test", event="toolbar:click")],
        )
        d = toolbar.to_dict()
        assert d["resizable"] is True


# =============================================================================
# Div Item Type Mapping Tests
# =============================================================================


class TestDivItemTypeMapping:
    """Test Div is properly registered in item type mapping."""

    def test_div_in_item_types(self) -> None:
        """Test Div type is recognized when creating from dict."""
        toolbar = Toolbar(
            position="top",
            items=[
                {"type": "div", "content": "<span>From dict</span>", "event": "toolbar:div"},
            ],
        )
        assert len(toolbar.items) == 1
        assert toolbar.items[0].type == "div"
        assert isinstance(toolbar.items[0], Div)

    def test_mixed_items_including_div(self) -> None:
        """Test toolbar with mixed item types including Div."""
        toolbar = Toolbar(
            position="top",
            items=[
                {"type": "button", "label": "Button", "event": "toolbar:button"},
                {"type": "div", "content": "<span>Div</span>", "event": "toolbar:div"},
                {"type": "select", "options": ["A", "B"], "event": "toolbar:select"},
            ],
        )
        assert len(toolbar.items) == 3
        assert toolbar.items[0].type == "button"
        assert toolbar.items[1].type == "div"
        assert toolbar.items[2].type == "select"


class TestDivDiscriminator:
    """Test Div in type discriminator."""

    def test_div_has_unique_type(self) -> None:
        """Test Div has unique type field."""
        div = Div(event="toolbar:div")
        assert div.type == "div"

    def test_all_types_including_div_unique(self) -> None:
        """Test all item types including Div have unique type values."""
        types = set()
        for cls in [
            Button,
            Select,
            MultiSelect,
            TextInput,
            NumberInput,
            DateInput,
            SliderInput,
            RangeInput,
            Div,
            Toggle,
            Checkbox,
            RadioGroup,
            TabGroup,
        ]:
            if cls == Button:
                inst = cls(label="Test", event="toolbar:click")
            elif cls in (Select, MultiSelect, RadioGroup, TabGroup):
                inst = cls(event="toolbar:click", options=[])
            else:
                inst = cls(event="toolbar:click")
            assert inst.type not in types, f"Duplicate type: {inst.type}"
            types.add(inst.type)


# =============================================================================
# Toggle Tests
# =============================================================================


class TestToggle:
    """Test the Toggle model (boolean switch)."""

    def test_type_is_toggle(self) -> None:
        """Test type field is 'toggle'."""
        toggle = Toggle(event="theme:toggle")
        assert toggle.type == "toggle"

    def test_default_value_false(self) -> None:
        """Test default value is False."""
        toggle = Toggle(event="theme:toggle")
        assert toggle.value is False

    def test_value_true(self) -> None:
        """Test value can be set to True."""
        toggle = Toggle(event="theme:toggle", value=True)
        assert toggle.value is True

    def test_html_contains_checkbox_input(self) -> None:
        """Test HTML contains checkbox input for toggle."""
        toggle = Toggle(event="theme:toggle")
        html = toggle.build_html()
        assert 'type="checkbox"' in html

    def test_html_contains_toggle_class(self) -> None:
        """Test HTML contains pywry-toggle class."""
        toggle = Toggle(event="theme:toggle")
        html = toggle.build_html()
        assert "pywry-toggle" in html
        assert "pywry-toggle-input" in html
        assert "pywry-toggle-slider" in html

    def test_html_checked_when_true(self) -> None:
        """Test HTML has checked attribute when value is True."""
        toggle = Toggle(event="theme:toggle", value=True)
        html = toggle.build_html()
        assert " checked" in html
        assert "pywry-toggle-checked" in html

    def test_html_not_checked_when_false(self) -> None:
        """Test HTML has no checked attribute when value is False."""
        toggle = Toggle(event="theme:toggle", value=False)
        html = toggle.build_html()
        # Should not have checked attribute (but may have "onchange" containing "checked")
        assert 'type="checkbox"' in html
        # The checked attribute should not be present as a standalone attribute
        assert "pywry-toggle-checked" not in html

    def test_html_with_label(self) -> None:
        """Test HTML wraps toggle with label."""
        toggle = Toggle(label="Dark Mode:", event="theme:toggle")
        html = toggle.build_html()
        assert "Dark Mode:" in html
        assert "pywry-input-label" in html

    def test_html_emits_event_with_value_and_component_id(self) -> None:
        """Test HTML contains emit call with value and componentId."""
        toggle = Toggle(event="theme:toggle")
        html = toggle.build_html()
        assert "pywry.emit" in html
        assert "theme:toggle" in html
        assert "value: this.checked" in html
        assert "componentId:" in html


# =============================================================================
# Checkbox Tests
# =============================================================================


class TestCheckbox:
    """Test the Checkbox model (single checkbox)."""

    def test_type_is_checkbox(self) -> None:
        """Test type field is 'checkbox'."""
        cb = Checkbox(event="settings:notify")
        assert cb.type == "checkbox"

    def test_default_value_false(self) -> None:
        """Test default value is False."""
        cb = Checkbox(event="settings:notify")
        assert cb.value is False

    def test_value_true(self) -> None:
        """Test value can be set to True."""
        cb = Checkbox(event="settings:notify", value=True)
        assert cb.value is True

    def test_html_contains_checkbox_input(self) -> None:
        """Test HTML contains checkbox input."""
        cb = Checkbox(event="settings:notify")
        html = cb.build_html()
        assert 'type="checkbox"' in html

    def test_html_contains_checkbox_class(self) -> None:
        """Test HTML contains pywry-checkbox class."""
        cb = Checkbox(event="settings:notify")
        html = cb.build_html()
        assert "pywry-checkbox" in html
        assert "pywry-checkbox-input" in html
        assert "pywry-checkbox-box" in html

    def test_html_checked_when_true(self) -> None:
        """Test HTML has checked attribute when value is True."""
        cb = Checkbox(event="settings:notify", value=True)
        html = cb.build_html()
        assert " checked" in html

    def test_html_contains_label_text(self) -> None:
        """Test HTML contains label text."""
        cb = Checkbox(label="Enable notifications", event="settings:notify")
        html = cb.build_html()
        assert "Enable notifications" in html
        assert "pywry-checkbox-label" in html

    def test_html_emits_event_with_value_and_component_id(self) -> None:
        """Test HTML contains emit call with value and componentId."""
        cb = Checkbox(event="settings:notify")
        html = cb.build_html()
        assert "pywry.emit" in html
        assert "settings:notify" in html
        assert "value: this.checked" in html
        assert "componentId:" in html

    def test_html_disabled_state(self) -> None:
        """Test HTML has disabled attribute when disabled."""
        cb = Checkbox(event="settings:notify", disabled=True)
        html = cb.build_html()
        assert " disabled" in html
        assert "pywry-disabled" in html


# =============================================================================
# RadioGroup Tests
# =============================================================================


class TestRadioGroup:
    """Test the RadioGroup model (radio button group)."""

    def test_type_is_radio(self) -> None:
        """Test type field is 'radio'."""
        rg = RadioGroup(event="view:change", options=[])
        assert rg.type == "radio"

    def test_default_direction_horizontal(self) -> None:
        """Test default direction is horizontal."""
        rg = RadioGroup(event="view:change", options=[])
        assert rg.direction == "horizontal"

    def test_direction_vertical(self) -> None:
        """Test direction can be set to vertical."""
        rg = RadioGroup(event="view:change", options=[], direction="vertical")
        assert rg.direction == "vertical"

    def test_options_from_option_objects(self) -> None:
        """Test options from Option objects."""
        rg = RadioGroup(
            event="view:change",
            options=[Option(label="List", value="list"), Option(label="Grid", value="grid")],
        )
        assert len(rg.options) == 2
        assert rg.options[0].label == "List"
        assert rg.options[0].value == "list"

    def test_options_from_dicts(self) -> None:
        """Test options from dict inputs."""
        rg = RadioGroup(
            event="view:change",
            options=[{"label": "List", "value": "list"}, {"label": "Grid", "value": "grid"}],
        )
        assert len(rg.options) == 2

    def test_options_from_strings(self) -> None:
        """Test options from string inputs."""
        rg = RadioGroup(event="view:change", options=["List", "Grid"])
        assert len(rg.options) == 2
        assert rg.options[0].label == "List"
        assert rg.options[0].value == "List"

    def test_selected_value(self) -> None:
        """Test selected value."""
        rg = RadioGroup(event="view:change", options=["List", "Grid"], selected="Grid")
        assert rg.selected == "Grid"

    def test_html_contains_radio_inputs(self) -> None:
        """Test HTML contains radio input elements."""
        rg = RadioGroup(event="view:change", options=["A", "B"])
        html = rg.build_html()
        assert 'type="radio"' in html
        assert html.count('type="radio"') == 2

    def test_html_contains_radio_group_class(self) -> None:
        """Test HTML contains pywry-radio-group class."""
        rg = RadioGroup(event="view:change", options=["A"])
        html = rg.build_html()
        assert "pywry-radio-group" in html

    def test_html_direction_class(self) -> None:
        """Test HTML contains direction class."""
        rg_h = RadioGroup(event="view:change", options=["A"], direction="horizontal")
        html_h = rg_h.build_html()
        assert "pywry-radio-horizontal" in html_h

        rg_v = RadioGroup(event="view:change", options=["A"], direction="vertical")
        html_v = rg_v.build_html()
        assert "pywry-radio-vertical" in html_v

    def test_html_marks_checked_option(self) -> None:
        """Test HTML marks selected option as checked."""
        rg = RadioGroup(event="view:change", options=["A", "B"], selected="B")
        html = rg.build_html()
        # The checked attribute should appear for option B
        assert " checked" in html

    def test_html_with_label(self) -> None:
        """Test HTML includes label."""
        rg = RadioGroup(label="View:", event="view:change", options=["A"])
        html = rg.build_html()
        assert "View:" in html
        assert "pywry-input-label" in html

    def test_html_contains_data_event(self) -> None:
        """Test HTML contains data-event attribute."""
        rg = RadioGroup(event="view:change", options=["A"])
        html = rg.build_html()
        assert 'data-event="view:change"' in html

    def test_html_emits_event_with_value_and_component_id(self) -> None:
        """Test HTML contains emit call with value and componentId."""
        rg = RadioGroup(event="view:change", options=["A"])
        html = rg.build_html()
        assert "pywry.emit" in html
        assert "view:change" in html
        assert "componentId:" in html


# =============================================================================
# TabGroup Tests
# =============================================================================


class TestTabGroup:
    """Test the TabGroup model (tab-style selection)."""

    def test_type_is_tab(self) -> None:
        """Test type field is 'tab'."""
        tg = TabGroup(event="view:change", options=[])
        assert tg.type == "tab"

    def test_default_size_md(self) -> None:
        """Test default size is 'md'."""
        tg = TabGroup(event="view:change", options=[])
        assert tg.size == "md"

    def test_size_variants(self) -> None:
        """Test size can be sm, md, or lg."""
        for size in ["sm", "md", "lg"]:
            tg = TabGroup(event="view:change", options=[], size=size)
            assert tg.size == size

    def test_options_from_option_objects(self) -> None:
        """Test options from Option objects."""
        tg = TabGroup(
            event="view:change",
            options=[Option(label="Table", value="table"), Option(label="Chart", value="chart")],
        )
        assert len(tg.options) == 2
        assert tg.options[0].label == "Table"
        assert tg.options[0].value == "table"

    def test_options_from_dicts(self) -> None:
        """Test options from dict inputs."""
        tg = TabGroup(
            event="view:change",
            options=[{"label": "Table", "value": "table"}, {"label": "Chart", "value": "chart"}],
        )
        assert len(tg.options) == 2

    def test_options_from_strings(self) -> None:
        """Test options from string inputs."""
        tg = TabGroup(event="view:change", options=["Table", "Chart"])
        assert len(tg.options) == 2
        assert tg.options[0].label == "Table"
        assert tg.options[0].value == "Table"

    def test_selected_value(self) -> None:
        """Test selected value."""
        tg = TabGroup(event="view:change", options=["Table", "Chart"], selected="Chart")
        assert tg.selected == "Chart"

    def test_html_contains_tab_buttons(self) -> None:
        """Test HTML contains button elements for tabs."""
        tg = TabGroup(event="view:change", options=["A", "B"])
        html = tg.build_html()
        assert "<button" in html
        assert html.count("<button") == 2

    def test_html_contains_tab_group_class(self) -> None:
        """Test HTML contains pywry-tab-group class."""
        tg = TabGroup(event="view:change", options=["A"])
        html = tg.build_html()
        assert "pywry-tab-group" in html
        assert "pywry-tab" in html

    def test_html_size_class(self) -> None:
        """Test HTML contains size class for non-default sizes."""
        tg_sm = TabGroup(event="view:change", options=["A"], size="sm")
        html_sm = tg_sm.build_html()
        assert "pywry-tab-sm" in html_sm

        tg_lg = TabGroup(event="view:change", options=["A"], size="lg")
        html_lg = tg_lg.build_html()
        assert "pywry-tab-lg" in html_lg

        tg_md = TabGroup(event="view:change", options=["A"], size="md")
        html_md = tg_md.build_html()
        # Default md size should not have size class
        assert "pywry-tab-sm" not in html_md
        assert "pywry-tab-lg" not in html_md

    def test_html_marks_active_tab(self) -> None:
        """Test HTML marks selected tab as active."""
        tg = TabGroup(event="view:change", options=["A", "B"], selected="B")
        html = tg.build_html()
        assert "pywry-tab-active" in html

    def test_html_contains_data_value(self) -> None:
        """Test HTML contains data-value on tab buttons."""
        tg = TabGroup(event="view:change", options=[Option(label="Table", value="table")])
        html = tg.build_html()
        assert 'data-value="table"' in html

    def test_html_contains_data_event(self) -> None:
        """Test HTML contains data-event attribute."""
        tg = TabGroup(event="view:change", options=["A"])
        html = tg.build_html()
        assert 'data-event="view:change"' in html

    def test_html_emits_event_with_value_and_component_id(self) -> None:
        """Test HTML contains emit call with value and componentId."""
        tg = TabGroup(event="view:change", options=["A"])
        html = tg.build_html()
        assert "pywry.emit" in html
        assert "view:change" in html
        assert "componentId:" in html

    def test_html_escapes_labels(self) -> None:
        """Test HTML escapes special characters in labels."""
        tg = TabGroup(event="view:change", options=["<script>"])
        html = tg.build_html()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


# =============================================================================
# Event Data Structure Tests
# =============================================================================


class TestEventDataStructure:
    """Test that each component emits events with the correct data structure.

    This validates that the JavaScript emit calls in HTML contain the expected
    data format for each component type.
    """

    def test_button_emits_component_id_and_custom_data(self) -> None:
        """Button emits componentId plus any custom data payload."""
        btn = Button(label="Export", event="export:csv", data={"format": "csv", "all": True})
        html = btn.build_html()
        # Button uses data-data attribute for custom payload
        assert 'data-data="' in html
        # Data should contain the custom payload
        assert "format" in html
        assert "csv" in html
        # Button has id attribute for componentId (added by toolbar-handlers.js)
        assert f'id="{btn.component_id}"' in html

    def test_select_emits_value_and_component_id(self) -> None:
        """Select emits {value, componentId}."""
        sel = Select(
            event="view:change",
            options=[Option(label="A", value="a"), Option(label="B", value="b")],
        )
        html = sel.build_html()
        # Select uses toolbar-handlers.js which adds componentId
        assert 'data-event="view:change"' in html
        assert f'id="{sel.component_id}"' in html

    def test_multiselect_emits_values_array_and_component_id(self) -> None:
        """MultiSelect emits {values: [...], componentId}."""
        ms = MultiSelect(
            event="filter:columns",
            options=[Option(label="A", value="a"), Option(label="B", value="b")],
            selected=["a"],
        )
        html = ms.build_html()
        # MultiSelect uses toolbar-handlers.js which emits values array
        assert 'data-event="filter:columns"' in html
        assert f'id="{ms.component_id}"' in html

    def test_text_input_emits_value_and_component_id(self) -> None:
        """TextInput emits {value, componentId}."""
        ti = TextInput(event="search:query", debounce=300)
        html = ti.build_html()
        # TextInput has inline emit with componentId
        assert "pywry.emit" in html
        assert "search:query" in html
        assert "value:" in html
        assert "componentId:" in html

    def test_number_input_emits_value_and_component_id(self) -> None:
        """NumberInput emits {value: <number>, componentId}."""
        ni = NumberInput(event="limit:set", value=10)
        html = ni.build_html()
        assert "pywry.emit" in html
        assert "limit:set" in html
        # Should parse as float/number
        assert "parseFloat" in html
        assert "componentId:" in html

    def test_date_input_emits_value_and_component_id(self) -> None:
        """DateInput emits {value: <date_string>, componentId}."""
        di = DateInput(event="date:start", value="2025-01-01")
        html = di.build_html()
        assert "pywry.emit" in html
        assert "date:start" in html
        assert "componentId:" in html

    def test_slider_input_emits_value_and_component_id(self) -> None:
        """SliderInput emits {value: <number>, componentId}."""
        si = SliderInput(event="zoom:level", value=50)
        html = si.build_html()
        assert "pywry.emit" in html
        assert "zoom:level" in html
        assert "parseFloat" in html
        assert "componentId:" in html

    def test_range_input_emits_start_end_and_component_id(self) -> None:
        """RangeInput emits {start: <number>, end: <number>, componentId}."""
        ri = RangeInput(event="filter:price", start=100, end=500)
        html = ri.build_html()
        assert "pywry.emit" in html
        assert "filter:price" in html
        assert "start:" in html
        assert "end:" in html
        assert "componentId:" in html

    def test_toggle_emits_value_and_component_id(self) -> None:
        """Toggle emits {value: <boolean>, componentId}."""
        toggle = Toggle(event="theme:dark", value=True)
        html = toggle.build_html()
        assert "pywry.emit" in html
        assert "theme:dark" in html
        assert "value: this.checked" in html
        assert "componentId:" in html

    def test_checkbox_emits_value_and_component_id(self) -> None:
        """Checkbox emits {value: <boolean>, componentId}."""
        cb = Checkbox(label="Enable", event="settings:enable", value=False)
        html = cb.build_html()
        assert "pywry.emit" in html
        assert "settings:enable" in html
        assert "value: this.checked" in html
        assert "componentId:" in html

    def test_radio_group_emits_value_and_component_id(self) -> None:
        """RadioGroup emits {value: <selected>, componentId}."""
        rg = RadioGroup(event="view:mode", options=["list", "grid"], selected="list")
        html = rg.build_html()
        assert "pywry.emit" in html
        assert "view:mode" in html
        assert "componentId:" in html

    def test_tab_group_emits_value_and_component_id(self) -> None:
        """TabGroup emits {value: <selected>, componentId}."""
        tg = TabGroup(event="view:tab", options=["A", "B"], selected="A")
        html = tg.build_html()
        assert "pywry.emit" in html
        assert "view:tab" in html
        assert "this.dataset.value" in html
        assert "componentId:" in html


# =============================================================================
# Component ID in HTML Tests
# =============================================================================


class TestComponentIdInHtml:
    """Test that all components include their component_id in generated HTML."""

    def test_button_has_id(self) -> None:
        """Button HTML includes id attribute."""
        btn = Button(label="Test", event="toolbar:click")
        html = btn.build_html()
        assert f'id="{btn.component_id}"' in html

    def test_select_has_id(self) -> None:
        """Select HTML includes id attribute."""
        sel = Select(event="view:change", options=["A"])
        html = sel.build_html()
        assert f'id="{sel.component_id}"' in html

    def test_multiselect_has_id(self) -> None:
        """MultiSelect HTML includes id attribute."""
        ms = MultiSelect(event="filter:cols", options=["A"])
        html = ms.build_html()
        assert f'id="{ms.component_id}"' in html

    def test_text_input_has_id(self) -> None:
        """TextInput HTML includes id attribute."""
        ti = TextInput(event="search:query")
        html = ti.build_html()
        assert f'id="{ti.component_id}"' in html

    def test_number_input_has_id(self) -> None:
        """NumberInput HTML includes id attribute."""
        ni = NumberInput(event="limit:set")
        html = ni.build_html()
        assert f'id="{ni.component_id}"' in html

    def test_date_input_has_id(self) -> None:
        """DateInput HTML includes id attribute."""
        di = DateInput(event="date:change")
        html = di.build_html()
        assert f'id="{di.component_id}"' in html

    def test_slider_input_has_id(self) -> None:
        """SliderInput HTML includes id attribute."""
        si = SliderInput(event="zoom:level")
        html = si.build_html()
        assert f'id="{si.component_id}"' in html

    def test_range_input_has_id(self) -> None:
        """RangeInput HTML includes id attribute on group container."""
        ri = RangeInput(event="filter:price")
        html = ri.build_html()
        assert f'id="{ri.component_id}"' in html

    def test_toggle_has_id(self) -> None:
        """Toggle HTML includes id attribute."""
        toggle = Toggle(event="theme:toggle")
        html = toggle.build_html()
        assert f'id="{toggle.component_id}"' in html

    def test_checkbox_has_id(self) -> None:
        """Checkbox HTML includes id attribute."""
        cb = Checkbox(event="settings:enable")
        html = cb.build_html()
        assert f'id="{cb.component_id}"' in html

    def test_radio_group_has_id(self) -> None:
        """RadioGroup HTML includes id attribute."""
        rg = RadioGroup(event="view:mode", options=["A"])
        html = rg.build_html()
        assert f'id="{rg.component_id}"' in html

    def test_tab_group_has_id(self) -> None:
        """TabGroup HTML includes id attribute."""
        tg = TabGroup(event="view:tab", options=["A"])
        html = tg.build_html()
        assert f'id="{tg.component_id}"' in html

    def test_div_has_id(self) -> None:
        """Div HTML includes id attribute."""
        div = Div(event="container:div", content="<p>Test</p>")
        html = div.build_html()
        assert f'id="{div.component_id}"' in html


# =============================================================================
# All Types in Discriminator Tests (updated)
# =============================================================================


class TestAllTypesDiscriminator:
    """Test that all toolbar item types are properly handled."""

    def test_all_item_types_have_unique_type(self) -> None:
        """All item types have unique type field values."""
        all_types = set()
        items = [
            Button(label="Test", event="toolbar:click"),
            Select(event="toolbar:select", options=[]),
            MultiSelect(event="toolbar:multiselect", options=[]),
            TextInput(event="toolbar:text"),
            NumberInput(event="toolbar:number"),
            DateInput(event="toolbar:date"),
            SliderInput(event="toolbar:slider"),
            RangeInput(event="toolbar:range"),
            Toggle(event="toolbar:toggle"),
            Checkbox(event="toolbar:checkbox"),
            RadioGroup(event="toolbar:radio", options=[]),
            TabGroup(event="toolbar:tab", options=[]),
            Div(event="toolbar:div"),
        ]
        for item in items:
            assert item.type not in all_types, f"Duplicate type: {item.type}"
            all_types.add(item.type)

    def test_all_types_build_valid_html(self) -> None:
        """All item types produce non-empty HTML."""
        items = [
            Button(label="Test", event="toolbar:click"),
            Select(event="toolbar:select", options=["A"]),
            MultiSelect(event="toolbar:multiselect", options=["A"]),
            TextInput(event="toolbar:text"),
            NumberInput(event="toolbar:number"),
            DateInput(event="toolbar:date"),
            SliderInput(event="toolbar:slider"),
            RangeInput(event="toolbar:range"),
            Toggle(event="toolbar:toggle"),
            Checkbox(label="Check", event="toolbar:checkbox"),
            RadioGroup(event="toolbar:radio", options=["A"]),
            TabGroup(event="toolbar:tab", options=["A"]),
            Div(event="toolbar:div", content="<p>Content</p>"),
        ]
        for item in items:
            html = item.build_html()
            assert html, f"{item.type} produced empty HTML"
            assert len(html) > 10, f"{item.type} HTML too short"


# =============================================================================
# Toolbar HTML Structure Tests
# =============================================================================


class TestToolbarHtmlStructure:
    """Test correct HTML div structure from Toolbar.build_html()."""

    def test_toolbar_outer_container_class(self) -> None:
        """Toolbar has pywry-toolbar class on outer container."""
        toolbar = Toolbar(items=[Button(label="Click", event="app:click")])
        html = toolbar.build_html()
        assert 'class="pywry-toolbar' in html

    def test_toolbar_position_class(self) -> None:
        """Toolbar has position-specific class."""
        for position in ["top", "bottom", "left", "right", "header", "footer", "inside"]:
            toolbar = Toolbar(
                position=position,  # type: ignore[arg-type]
                items=[Button(label="Click", event="app:click")],
            )
            html = toolbar.build_html()
            assert f"pywry-toolbar-{position}" in html

    def test_toolbar_content_wrapper(self) -> None:
        """Toolbar items are wrapped in pywry-toolbar-content div."""
        toolbar = Toolbar(items=[Button(label="Click", event="app:click")])
        html = toolbar.build_html()
        assert 'class="pywry-toolbar-content"' in html

    def test_toolbar_has_component_id(self) -> None:
        """Toolbar has both id and data-component-id attributes."""
        toolbar = Toolbar(items=[Button(label="Click", event="app:click")])
        html = toolbar.build_html()
        assert f'id="{toolbar.component_id}"' in html
        assert f'data-component-id="{toolbar.component_id}"' in html

    def test_toolbar_has_position_data_attribute(self) -> None:
        """Toolbar has data-position attribute."""
        toolbar = Toolbar(position="left", items=[Button(label="X", event="app:x")])
        html = toolbar.build_html()
        assert 'data-position="left"' in html

    def test_empty_toolbar_returns_empty_string(self) -> None:
        """Toolbar with no items returns empty string."""
        toolbar = Toolbar(items=[])
        html = toolbar.build_html()
        assert html == ""

    def test_collapsible_toolbar_has_toggle_button(self) -> None:
        """Collapsible toolbar includes toggle button."""
        toolbar = Toolbar(
            items=[Button(label="Click", event="app:click")],
            collapsible=True,
        )
        html = toolbar.build_html()
        assert 'class="pywry-toolbar-toggle"' in html
        assert 'data-collapsible="true"' in html
        assert 'aria-expanded="true"' in html

    def test_resizable_toolbar_has_resize_handle(self) -> None:
        """Resizable toolbar includes resize handle."""
        toolbar = Toolbar(
            items=[Button(label="Click", event="app:click")],
            resizable=True,
        )
        html = toolbar.build_html()
        assert 'class="pywry-resize-handle"' in html
        assert 'data-resizable="true"' in html

    def test_toolbar_custom_class_name(self) -> None:
        """Toolbar custom class_name is added to classes."""
        toolbar = Toolbar(
            items=[Button(label="X", event="app:x")],
            class_name="my-custom-toolbar",
        )
        html = toolbar.build_html()
        assert "my-custom-toolbar" in html

    def test_toolbar_style_on_inside_position(self) -> None:
        """For 'inside' position, style goes on outer div."""
        toolbar = Toolbar(
            position="inside",
            items=[Button(label="X", event="app:x")],
            style="top: 10px; right: 10px;",
        )
        html = toolbar.build_html()
        # Style should be on outer div, not content div
        assert 'style="top: 10px; right: 10px;"' in html

    def test_toolbar_style_on_other_positions(self) -> None:
        """For non-inside positions, style goes on content wrapper."""
        toolbar = Toolbar(
            position="top",
            items=[Button(label="X", event="app:x")],
            style="justify-content: center;",
        )
        html = toolbar.build_html()
        # Style should be on content div
        assert 'class="pywry-toolbar-content" style="justify-content: center;"' in html


class TestToolbarNesting:
    """Test correct nesting of Div children within toolbars."""

    def test_div_has_pywry_div_class(self) -> None:
        """Div container has pywry-div class."""
        div = Div(content="<span>Hello</span>", event="app:container")
        html = div.build_html()
        assert 'class="pywry-div"' in html

    def test_div_custom_class_name(self) -> None:
        """Div custom class_name is added to classes."""
        div = Div(
            content="<span>Hello</span>",
            event="app:container",
            class_name="my-group",
        )
        html = div.build_html()
        assert "pywry-div" in html
        assert "my-group" in html

    def test_div_with_children(self) -> None:
        """Div renders nested children components."""
        div = Div(
            event="app:group",
            children=[
                Button(label="Btn1", event="app:btn1"),
                Button(label="Btn2", event="app:btn2"),
            ],
        )
        html = div.build_html()
        assert "Btn1" in html
        assert "Btn2" in html
        # Should have button tags inside div
        assert html.count("<button") == 2

    def test_div_nested_divs(self) -> None:
        """Div can contain nested Div children."""
        outer = Div(
            event="app:outer",
            class_name="outer-group",
            children=[
                Div(
                    event="app:inner",
                    class_name="inner-group",
                    children=[Button(label="Deep", event="app:deep")],
                ),
            ],
        )
        html = outer.build_html()
        assert "outer-group" in html
        assert "inner-group" in html
        assert "Deep" in html
        # Two div containers (outer + inner)
        assert html.count('class="pywry-div') == 2

    def test_div_parent_id_propagation(self) -> None:
        """Div passes parent_id to nested Div children."""
        outer = Div(
            event="app:outer",
            component_id="outer-div-123",
            children=[
                Div(event="app:inner", class_name="inner"),
            ],
        )
        html = outer.build_html()
        # Inner div should have data-parent-id pointing to outer
        assert 'data-parent-id="outer-div-123"' in html

    def test_div_content_and_children_combined(self) -> None:
        """Div renders both content and children."""
        div = Div(
            event="app:combined",
            content="<h3>Header</h3>",
            children=[Button(label="Action", event="app:action")],
        )
        html = div.build_html()
        assert "<h3>Header</h3>" in html
        assert "Action" in html

    def test_toolbar_with_nested_divs(self) -> None:
        """Toolbar correctly renders Div items with nested children."""
        toolbar = Toolbar(
            items=[
                Div(
                    event="app:controls",
                    class_name="control-group",
                    children=[
                        Button(label="Save", event="app:save"),
                        Button(label="Cancel", event="app:cancel"),
                    ],
                ),
                Select(event="app:mode", options=["A", "B"]),
            ],
        )
        html = toolbar.build_html()
        # Verify structure
        assert 'class="pywry-toolbar' in html
        assert "control-group" in html
        assert "Save" in html
        assert "Cancel" in html
        # Select renders as pywry-dropdown (custom dropdown component)
        assert 'class="pywry-dropdown"' in html


class TestBuildToolbarsHtmlStructure:
    """Test build_toolbars_html for multiple toolbars structure."""

    def test_single_toolbar_structure(self) -> None:
        """Single toolbar builds correctly."""
        toolbar = Toolbar(items=[Button(label="A", event="app:a")])
        html = build_toolbars_html([toolbar])
        assert 'class="pywry-toolbar ' in html
        # One outer toolbar container
        assert html.count('class="pywry-toolbar ') == 1

    def test_multiple_toolbars_concatenated(self) -> None:
        """Multiple toolbars are concatenated in order."""
        toolbar1 = Toolbar(items=[Button(label="First", event="app:first")])
        toolbar2 = Toolbar(items=[Button(label="Second", event="app:second")])
        html = build_toolbars_html([toolbar1, toolbar2])
        # Both toolbars present (use exact class prefix to avoid matching position classes)
        assert html.count('class="pywry-toolbar ') == 2
        assert "First" in html
        assert "Second" in html
        # Order preserved (First before Second)
        assert html.index("First") < html.index("Second")

    def test_empty_list_returns_empty_string(self) -> None:
        """Empty toolbar list returns empty string."""
        html = build_toolbars_html([])
        assert html == ""

    def test_none_returns_empty_string(self) -> None:
        """None input returns empty string."""
        html = build_toolbars_html(None)
        assert html == ""

    def test_dict_toolbars_converted(self) -> None:
        """Dict-based toolbar configs are converted to Toolbar objects."""
        html = build_toolbars_html(
            [
                {"items": [{"type": "button", "label": "DictBtn", "event": "app:dict"}]},
            ]
        )
        assert "DictBtn" in html

    def test_mixed_toolbar_and_dict(self) -> None:
        """Mix of Toolbar objects and dicts works correctly."""
        toolbar = Toolbar(items=[Button(label="Model", event="app:model")])
        html = build_toolbars_html(
            [
                toolbar,
                {"items": [{"type": "button", "label": "Dict", "event": "app:dict"}]},
            ]
        )
        assert "Model" in html
        assert "Dict" in html


class TestWrapContentWithToolbars:
    """Test wrap_content_with_toolbars layout structure."""

    def test_no_toolbars_wraps_in_pywry_content(self) -> None:
        """Content without toolbars is wrapped in pywry-content."""
        from pywry.toolbar import wrap_content_with_toolbars

        html = wrap_content_with_toolbars("<div>My Content</div>")
        assert (
            html
            == "<div class='pywry-content'><div>My Content</div></div><div class='pywry-toast-container pywry-toast-container--top-right' aria-label='Notifications'></div>"
        )

    def test_top_toolbar_position(self) -> None:
        """Top toolbar appears before content."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbar = Toolbar(position="top", items=[Button(label="Top", event="app:top")])
        html = wrap_content_with_toolbars("<p>Content</p>", toolbars=[toolbar])
        assert "pywry-wrapper-top" in html
        # Top toolbar should come before pywry-content
        top_idx = html.index("Top")
        content_idx = html.index("<p>Content</p>")
        assert top_idx < content_idx

    def test_bottom_toolbar_position(self) -> None:
        """Bottom toolbar appears after content."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbar = Toolbar(position="bottom", items=[Button(label="Bottom", event="app:bottom")])
        html = wrap_content_with_toolbars("<p>Content</p>", toolbars=[toolbar])
        # Bottom toolbar should come after pywry-content
        bottom_idx = html.index("Bottom")
        content_idx = html.index("<p>Content</p>")
        assert bottom_idx > content_idx

    def test_header_footer_outermost(self) -> None:
        """Header/footer are outermost wrappers."""
        from pywry.toolbar import wrap_content_with_toolbars

        header = Toolbar(position="header", items=[Button(label="Header", event="app:header")])
        footer = Toolbar(position="footer", items=[Button(label="Footer", event="app:footer")])
        html = wrap_content_with_toolbars("<p>Content</p>", toolbars=[header, footer])
        assert "pywry-wrapper-header" in html
        # Header first, footer last in document order
        header_idx = html.index("Header")
        footer_idx = html.index("Footer")
        content_idx = html.index("<p>Content</p>")
        assert header_idx < content_idx < footer_idx

    def test_left_right_extend_height(self) -> None:
        """Left/right toolbars use wrapper-left class."""
        from pywry.toolbar import wrap_content_with_toolbars

        left = Toolbar(position="left", items=[Button(label="Left", event="app:left")])
        right = Toolbar(position="right", items=[Button(label="Right", event="app:right")])
        html = wrap_content_with_toolbars("<p>Content</p>", toolbars=[left, right])
        assert "pywry-wrapper-left" in html
        # Left before content, right after
        left_idx = html.index("Left")
        right_idx = html.index("Right")
        content_idx = html.index("<p>Content</p>")
        assert left_idx < content_idx < right_idx

    def test_inside_toolbar_overlays_content(self) -> None:
        """Inside toolbar uses wrapper-inside class."""
        from pywry.toolbar import wrap_content_with_toolbars

        inside = Toolbar(position="inside", items=[Button(label="Inside", event="app:inside")])
        html = wrap_content_with_toolbars("<p>Content</p>", toolbars=[inside])
        assert "pywry-wrapper-inside" in html

    def test_multiple_positions_nested_correctly(self) -> None:
        """Multiple positions nest in correct order: header > left/right > top/bottom > inside > content."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbars = [
            Toolbar(position="header", items=[Button(label="H", event="app:h")]),
            Toolbar(position="footer", items=[Button(label="F", event="app:f")]),
            Toolbar(position="left", items=[Button(label="L", event="app:l")]),
            Toolbar(position="right", items=[Button(label="R", event="app:r")]),
            Toolbar(position="top", items=[Button(label="T", event="app:t")]),
            Toolbar(position="bottom", items=[Button(label="B", event="app:b")]),
            Toolbar(position="inside", items=[Button(label="I", event="app:i")]),
        ]
        html = wrap_content_with_toolbars("<p>C</p>", toolbars=toolbars)
        # All wrappers present
        assert "pywry-wrapper-header" in html
        assert "pywry-wrapper-left" in html
        assert "pywry-wrapper-top" in html
        assert "pywry-wrapper-inside" in html
        # Content is innermost
        assert "pywry-content" in html

    def test_stacked_top_toolbars_order_preserved(self) -> None:
        """Multiple top toolbars are stacked in order."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbar1 = Toolbar(position="top", items=[Button(label="TopA", event="app:a")])
        toolbar2 = Toolbar(position="top", items=[Button(label="TopB", event="app:b")])
        html = wrap_content_with_toolbars("<p>C</p>", toolbars=[toolbar1, toolbar2])
        # Both present
        assert "TopA" in html
        assert "TopB" in html
        # Order preserved
        assert html.index("TopA") < html.index("TopB")

    def test_extra_top_html_prepended(self) -> None:
        """extra_top_html is prepended to top toolbar area."""
        from pywry.toolbar import wrap_content_with_toolbars

        html = wrap_content_with_toolbars(
            "<p>Content</p>",
            toolbars=[],
            extra_top_html="<div class='custom-header'>Custom</div>",
        )
        assert "custom-header" in html
        # Custom header before content
        custom_idx = html.index("Custom")
        content_idx = html.index("Content")
        assert custom_idx < content_idx


class TestComponentOrderInToolbar:
    """Test that component order is preserved within toolbars."""

    def test_items_render_in_order(self) -> None:
        """Toolbar items render in the order they were added."""
        toolbar = Toolbar(
            items=[
                Button(label="Alpha", event="app:alpha"),
                Select(event="app:sel", options=["X"]),
                Button(label="Beta", event="app:beta"),
                TextInput(event="app:text"),
                Button(label="Gamma", event="app:gamma"),
            ],
        )
        html = toolbar.build_html()
        # Check order
        alpha_idx = html.index("Alpha")
        beta_idx = html.index("Beta")
        gamma_idx = html.index("Gamma")
        assert alpha_idx < beta_idx < gamma_idx

    def test_nested_children_order_preserved(self) -> None:
        """Nested Div children maintain order."""
        div = Div(
            event="app:group",
            children=[
                Button(label="First", event="app:first"),
                Button(label="Second", event="app:second"),
                Button(label="Third", event="app:third"),
            ],
        )
        html = div.build_html()
        first_idx = html.index("First")
        second_idx = html.index("Second")
        third_idx = html.index("Third")
        assert first_idx < second_idx < third_idx


# =============================================================================
# Complex Stacked Toolbar Layout Tests
# =============================================================================


class TestStackedToolbarsSamePosition:
    """Test multiple toolbars stacked at the same position."""

    def test_two_top_toolbars_stacked(self) -> None:
        """Two top toolbars are rendered in order."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbar1 = Toolbar(position="top", items=[Button(label="TopRow1", event="app:t1")])
        toolbar2 = Toolbar(position="top", items=[Button(label="TopRow2", event="app:t2")])
        html = wrap_content_with_toolbars("<p>C</p>", toolbars=[toolbar1, toolbar2])

        assert "TopRow1" in html
        assert "TopRow2" in html
        assert html.index("TopRow1") < html.index("TopRow2")
        # Both should be before content
        assert html.index("TopRow2") < html.index("<p>C</p>")

    def test_three_left_toolbars_stacked(self) -> None:
        """Three left toolbars are rendered in order."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbars = [
            Toolbar(position="left", items=[Button(label="Left1", event="app:l1")]),
            Toolbar(position="left", items=[Button(label="Left2", event="app:l2")]),
            Toolbar(position="left", items=[Button(label="Left3", event="app:l3")]),
        ]
        html = wrap_content_with_toolbars("<p>C</p>", toolbars=toolbars)

        assert html.index("Left1") < html.index("Left2") < html.index("Left3")
        # All left toolbars before content
        assert html.index("Left3") < html.index("<p>C</p>")

    def test_two_bottom_toolbars_stacked(self) -> None:
        """Two bottom toolbars are rendered after content in order."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbar1 = Toolbar(position="bottom", items=[Button(label="Bot1", event="app:b1")])
        toolbar2 = Toolbar(position="bottom", items=[Button(label="Bot2", event="app:b2")])
        html = wrap_content_with_toolbars("<p>C</p>", toolbars=[toolbar1, toolbar2])

        # Both after content
        assert html.index("<p>C</p>") < html.index("Bot1")
        assert html.index("Bot1") < html.index("Bot2")

    def test_two_right_toolbars_stacked(self) -> None:
        """Two right toolbars are rendered after content in order."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbar1 = Toolbar(position="right", items=[Button(label="Right1", event="app:r1")])
        toolbar2 = Toolbar(position="right", items=[Button(label="Right2", event="app:r2")])
        html = wrap_content_with_toolbars("<p>C</p>", toolbars=[toolbar1, toolbar2])

        # Both after content (right side)
        assert html.index("<p>C</p>") < html.index("Right1")
        assert html.index("Right1") < html.index("Right2")

    def test_two_inside_toolbars_stacked(self) -> None:
        """Two inside toolbars overlay content in order."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbar1 = Toolbar(
            position="inside",
            items=[Button(label="Overlay1", event="app:o1")],
            style="top: 10px; left: 10px;",
        )
        toolbar2 = Toolbar(
            position="inside",
            items=[Button(label="Overlay2", event="app:o2")],
            style="top: 10px; right: 10px;",
        )
        html = wrap_content_with_toolbars("<p>C</p>", toolbars=[toolbar1, toolbar2])

        assert "pywry-wrapper-inside" in html
        assert "Overlay1" in html
        assert "Overlay2" in html
        # Inside toolbars come before content in HTML
        assert html.index("Overlay1") < html.index("<p>C</p>")


class TestMixedPositionLayouts:
    """Test layouts combining toolbars at different positions."""

    def test_top_and_bottom(self) -> None:
        """Top and bottom toolbars sandwich content."""
        from pywry.toolbar import wrap_content_with_toolbars

        top = Toolbar(position="top", items=[Button(label="TopNav", event="app:top")])
        bottom = Toolbar(position="bottom", items=[Button(label="Status", event="app:status")])
        html = wrap_content_with_toolbars("<main>Content</main>", toolbars=[top, bottom])

        top_idx = html.index("TopNav")
        content_idx = html.index("<main>Content</main>")
        bottom_idx = html.index("Status")
        assert top_idx < content_idx < bottom_idx

    def test_left_and_right(self) -> None:
        """Left and right toolbars flank content."""
        from pywry.toolbar import wrap_content_with_toolbars

        left = Toolbar(position="left", items=[Button(label="Sidebar", event="app:side")])
        right = Toolbar(position="right", items=[Button(label="Panel", event="app:panel")])
        html = wrap_content_with_toolbars("<main>Content</main>", toolbars=[left, right])

        left_idx = html.index("Sidebar")
        content_idx = html.index("<main>Content</main>")
        right_idx = html.index("Panel")
        assert left_idx < content_idx < right_idx

    def test_header_and_footer(self) -> None:
        """Header and footer wrap entire layout."""
        from pywry.toolbar import wrap_content_with_toolbars

        header = Toolbar(position="header", items=[Button(label="Logo", event="app:logo")])
        footer = Toolbar(position="footer", items=[Button(label="Copyright", event="app:copy")])
        html = wrap_content_with_toolbars("<main>Content</main>", toolbars=[header, footer])

        # Header first, footer last
        header_idx = html.index("Logo")
        content_idx = html.index("<main>Content</main>")
        footer_idx = html.index("Copyright")
        assert header_idx < content_idx < footer_idx
        # Verify header wrapper is outermost
        assert "pywry-wrapper-header" in html

    def test_all_edge_positions(self) -> None:
        """All four edge positions (top, bottom, left, right)."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbars = [
            Toolbar(position="top", items=[Button(label="T", event="app:t")]),
            Toolbar(position="bottom", items=[Button(label="B", event="app:b")]),
            Toolbar(position="left", items=[Button(label="L", event="app:l")]),
            Toolbar(position="right", items=[Button(label="R", event="app:r")]),
        ]
        html = wrap_content_with_toolbars("<div>C</div>", toolbars=toolbars)

        # Structure: left > top > content > bottom > right
        l_idx = html.index(">L<")
        t_idx = html.index(">T<")
        c_idx = html.index("<div>C</div>")
        b_idx = html.index(">B<")
        r_idx = html.index(">R<")
        assert l_idx < t_idx < c_idx < b_idx < r_idx

    def test_header_footer_with_inner_toolbars(self) -> None:
        """Header/footer wrap inner top/bottom toolbars."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbars = [
            Toolbar(position="header", items=[Button(label="H", event="app:h")]),
            Toolbar(position="footer", items=[Button(label="F", event="app:f")]),
            Toolbar(position="top", items=[Button(label="T", event="app:t")]),
            Toolbar(position="bottom", items=[Button(label="B", event="app:b")]),
        ]
        html = wrap_content_with_toolbars("<div>C</div>", toolbars=toolbars)

        # Header outermost top, Footer outermost bottom
        h_idx = html.index(">H<")
        t_idx = html.index(">T<")
        c_idx = html.index("<div>C</div>")
        b_idx = html.index(">B<")
        f_idx = html.index(">F<")
        assert h_idx < t_idx < c_idx < b_idx < f_idx


class TestComplexRealWorldLayouts:
    """Test complex layouts similar to real applications."""

    def test_dashboard_layout(self) -> None:
        """Dashboard: header + left sidebar + top toolbar + content + bottom status."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbars = [
            Toolbar(
                position="header",
                items=[
                    Button(label="Logo", event="app:logo"),
                    Button(label="Settings", event="app:settings"),
                ],
            ),
            Toolbar(
                position="left",
                items=[
                    Button(label="Home", event="nav:home"),
                    Button(label="Reports", event="nav:reports"),
                    Button(label="Admin", event="nav:admin"),
                ],
            ),
            Toolbar(
                position="top",
                items=[
                    Select(event="app:view", options=["Table", "Chart", "Grid"]),
                    Button(label="Refresh", event="app:refresh"),
                ],
            ),
            Toolbar(
                position="bottom",
                items=[TextInput(event="app:search", placeholder="Search...")],
            ),
        ]
        html = wrap_content_with_toolbars(
            "<div id='dashboard'>Dashboard Content</div>", toolbars=toolbars
        )

        # All components present
        assert "Logo" in html
        assert "Settings" in html
        assert "Home" in html
        assert "Reports" in html
        assert "Admin" in html
        assert "Refresh" in html
        assert "Dashboard Content" in html

        # Layout order
        assert html.index("Logo") < html.index("Home")  # Header before left
        assert html.index("Home") < html.index("Refresh")  # Left before top
        assert html.index("Refresh") < html.index("Dashboard Content")  # Top before content

    def test_editor_layout_with_inside_toolbar(self) -> None:
        """Editor: header + floating inside toolbar + content + bottom status."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbars = [
            Toolbar(
                position="header",
                items=[
                    Button(label="File", event="menu:file"),
                    Button(label="Edit", event="menu:edit"),
                ],
            ),
            Toolbar(
                position="inside",
                items=[
                    Button(label="Bold", event="format:bold"),
                    Button(label="Italic", event="format:italic"),
                ],
                style="top: 40px; right: 20px;",
            ),
            Toolbar(
                position="bottom",
                items=[Button(label="Ln 1, Col 1", event="status:position")],
            ),
        ]
        html = wrap_content_with_toolbars("<textarea>Editor</textarea>", toolbars=toolbars)

        # All present
        assert "File" in html
        assert "Bold" in html
        assert "Italic" in html
        assert "Ln 1, Col 1" in html
        assert "pywry-wrapper-inside" in html
        assert "pywry-wrapper-header" in html

    def test_chart_with_all_seven_positions(self) -> None:
        """Chart viewer with all seven positions populated."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbars = [
            Toolbar(position="header", items=[Button(label="HEADER", event="app:header")]),
            Toolbar(position="footer", items=[Button(label="FOOTER", event="app:footer")]),
            Toolbar(position="left", items=[Button(label="LEFT", event="app:left")]),
            Toolbar(position="right", items=[Button(label="RIGHT", event="app:right")]),
            Toolbar(position="top", items=[Button(label="TOP", event="app:top")]),
            Toolbar(position="bottom", items=[Button(label="BOTTOM", event="app:bottom")]),
            Toolbar(
                position="inside",
                items=[Button(label="INSIDE", event="app:inside")],
                style="position: absolute; top: 10px; left: 10px;",
            ),
        ]
        html = wrap_content_with_toolbars("<canvas id='chart'></canvas>", toolbars=toolbars)

        # All wrappers present
        assert "pywry-wrapper-header" in html
        assert "pywry-wrapper-left" in html
        assert "pywry-wrapper-top" in html
        assert "pywry-wrapper-inside" in html
        assert "pywry-content" in html

        # All labels present
        for label in ["HEADER", "FOOTER", "LEFT", "RIGHT", "TOP", "BOTTOM", "INSIDE"]:
            assert label in html

        # Verify nesting order: HEADER > LEFT > TOP > INSIDE > content
        header_idx = html.index("HEADER")
        left_idx = html.index("LEFT")
        top_idx = html.index("TOP")
        inside_idx = html.index("INSIDE")
        content_idx = html.index("<canvas id='chart'>")
        bottom_idx = html.index("BOTTOM")
        right_idx = html.index("RIGHT")
        footer_idx = html.index("FOOTER")

        assert header_idx < left_idx < top_idx < inside_idx < content_idx
        assert content_idx < bottom_idx < right_idx < footer_idx

    def test_stacked_toolbars_at_multiple_positions(self) -> None:
        """Multiple toolbars stacked at multiple positions simultaneously."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbars = [
            # Two top toolbars
            Toolbar(position="top", items=[Button(label="Top1", event="app:t1")]),
            Toolbar(position="top", items=[Button(label="Top2", event="app:t2")]),
            # Two left toolbars
            Toolbar(position="left", items=[Button(label="Left1", event="app:l1")]),
            Toolbar(position="left", items=[Button(label="Left2", event="app:l2")]),
            # Two bottom toolbars
            Toolbar(position="bottom", items=[Button(label="Bot1", event="app:b1")]),
            Toolbar(position="bottom", items=[Button(label="Bot2", event="app:b2")]),
        ]
        html = wrap_content_with_toolbars("<div>Content</div>", toolbars=toolbars)

        # Verify stacking order within each position
        assert html.index("Left1") < html.index("Left2")
        assert html.index("Top1") < html.index("Top2")
        assert html.index("Bot1") < html.index("Bot2")

        # Verify inter-position order
        assert html.index("Left2") < html.index("Top1")  # Left before top
        assert html.index("Top2") < html.index("<div>Content</div>")  # Top before content
        assert html.index("<div>Content</div>") < html.index("Bot1")  # Content before bottom


class TestToolbarStackWithDifferentComponents:
    """Test stacked toolbars with varying component types."""

    def test_mixed_components_across_toolbars(self) -> None:
        """Different component types in different toolbars."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbars = [
            Toolbar(
                position="top",
                items=[
                    Button(label="Action", event="app:action"),
                    Toggle(label="Dark Mode", event="app:dark"),
                ],
            ),
            Toolbar(
                position="top",
                items=[
                    Select(event="app:view", options=["List", "Grid", "Card"]),
                    TextInput(event="app:filter", placeholder="Filter..."),
                ],
            ),
            Toolbar(
                position="left",
                items=[
                    RadioGroup(event="nav:section", options=["Home", "Settings", "Help"]),
                ],
            ),
        ]
        html = wrap_content_with_toolbars("<div>App</div>", toolbars=toolbars)

        # All component types rendered
        assert "Action" in html
        assert "Dark Mode" in html
        assert 'class="pywry-dropdown"' in html  # Select
        assert 'placeholder="Filter..."' in html
        assert "pywry-radio-group" in html

    def test_toolbar_with_nested_divs_in_stack(self) -> None:
        """Stacked toolbars with nested Div groupings."""
        from pywry.toolbar import wrap_content_with_toolbars

        toolbars = [
            Toolbar(
                position="top",
                items=[
                    Div(
                        event="app:file-group",
                        class_name="file-actions",
                        children=[
                            Button(label="New", event="file:new"),
                            Button(label="Open", event="file:open"),
                            Button(label="Save", event="file:save"),
                        ],
                    ),
                    Div(
                        event="app:edit-group",
                        class_name="edit-actions",
                        children=[
                            Button(label="Undo", event="edit:undo"),
                            Button(label="Redo", event="edit:redo"),
                        ],
                    ),
                ],
            ),
            Toolbar(
                position="top",
                items=[
                    SliderInput(event="view:zoom", min=50, max=200, value=100),
                ],
            ),
        ]
        html = wrap_content_with_toolbars("<canvas>Editor</canvas>", toolbars=toolbars)

        # Div groups present
        assert "file-actions" in html
        assert "edit-actions" in html
        # Buttons within groups
        assert "New" in html
        assert "Open" in html
        assert "Undo" in html
        # Slider in second toolbar
        assert 'class="pywry-input pywry-input-range"' in html

        # Order: New < Open < Save < Undo < Redo < slider
        assert html.index("New") < html.index("Open") < html.index("Save")
        assert html.index("Save") < html.index("Undo") < html.index("Redo")


class TestToolbarPositionSpecificBehavior:
    """Test position-specific rendering behavior."""

    def test_inside_position_has_absolute_style(self) -> None:
        """Inside toolbar style is on outer div for absolute positioning."""
        toolbar = Toolbar(
            position="inside",
            items=[Button(label="Float", event="app:float")],
            style="top: 10px; right: 10px;",
        )
        html = toolbar.build_html()

        # Style should be on the outer toolbar div, not content div
        # Pattern: <div class="pywry-toolbar..." style="top: 10px; right: 10px;">
        assert 'class="pywry-toolbar pywry-toolbar-inside"' in html
        assert 'style="top: 10px; right: 10px;"' in html

    def test_non_inside_position_style_on_content(self) -> None:
        """Non-inside toolbar style is on content div for flex alignment."""
        toolbar = Toolbar(
            position="top",
            items=[Button(label="Btn", event="app:btn")],
            style="justify-content: center; gap: 10px;",
        )
        html = toolbar.build_html()

        # Style should be on content div
        assert 'class="pywry-toolbar-content" style="justify-content: center; gap: 10px;"' in html

    def test_each_position_has_correct_class(self) -> None:
        """Each position produces correct position class."""
        positions = ["top", "bottom", "left", "right", "header", "footer", "inside"]
        for pos in positions:
            toolbar = Toolbar(
                position=pos,  # type: ignore[arg-type]
                items=[Button(label="X", event="app:x")],
            )
            html = toolbar.build_html()
            assert f"pywry-toolbar-{pos}" in html

    def test_collapsible_works_at_each_position(self) -> None:
        """Collapsible attribute works at all positions."""
        for pos in ["top", "left", "right"]:
            toolbar = Toolbar(
                position=pos,  # type: ignore[arg-type]
                items=[Button(label="X", event="app:x")],
                collapsible=True,
            )
            html = toolbar.build_html()
            assert 'data-collapsible="true"' in html
            assert "pywry-toolbar-toggle" in html

    def test_resizable_works_at_each_position(self) -> None:
        """Resizable attribute works at all positions."""
        for pos in ["left", "right", "bottom"]:
            toolbar = Toolbar(
                position=pos,  # type: ignore[arg-type]
                items=[Button(label="X", event="app:x")],
                resizable=True,
            )
            html = toolbar.build_html()
            assert 'data-resizable="true"' in html
            assert "pywry-resize-handle" in html


class TestToolbarIdPropagation:
    """Test component ID propagation through stacked toolbars."""

    def test_each_toolbar_has_unique_id(self) -> None:
        """Each toolbar in a stack has a unique component ID."""
        toolbar1 = Toolbar(items=[Button(label="A", event="app:a")])
        toolbar2 = Toolbar(items=[Button(label="B", event="app:b")])
        toolbar3 = Toolbar(items=[Button(label="C", event="app:c")])

        ids = {toolbar1.component_id, toolbar2.component_id, toolbar3.component_id}
        assert len(ids) == 3  # All unique

    def test_toolbar_id_in_html(self) -> None:
        """Toolbar ID appears in rendered HTML."""
        toolbar = Toolbar(
            component_id="my-toolbar-123",
            items=[Button(label="X", event="app:x")],
        )
        html = toolbar.build_html()

        assert 'id="my-toolbar-123"' in html
        assert 'data-component-id="my-toolbar-123"' in html

    def test_div_parent_id_chain(self) -> None:
        """Div children receive parent toolbar ID."""
        toolbar = Toolbar(
            component_id="parent-toolbar",
            items=[
                Div(
                    event="app:group",
                    class_name="group",
                    children=[Button(label="Nested", event="app:nested")],
                ),
            ],
        )
        html = toolbar.build_html()

        # Div should have data-parent-id pointing to toolbar
        assert 'data-parent-id="parent-toolbar"' in html

    def test_nested_div_chain(self) -> None:
        """Nested Divs maintain parent ID chain."""
        toolbar = Toolbar(
            component_id="root",
            items=[
                Div(
                    event="app:level1",
                    component_id="level1-div",
                    children=[
                        Div(
                            event="app:level2",
                            component_id="level2-div",
                            children=[Button(label="Deep", event="app:deep")],
                        ),
                    ],
                ),
            ],
        )
        html = toolbar.build_html()

        # Level 1 div has root as parent
        assert 'id="level1-div"' in html
        assert 'data-parent-id="root"' in html
        # Level 2 div has level1 as parent
        assert 'id="level2-div"' in html
        assert 'data-parent-id="level1-div"' in html
