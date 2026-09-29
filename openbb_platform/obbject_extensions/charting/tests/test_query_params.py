"""Tests for ``openbb_charting.query_params``."""

from __future__ import annotations

import pytest

from openbb_charting.query_params import (
    ChartParams,
    ChartQueryParams,
    EquityPriceHistoricalChartQueryParams,
    IndicatorsParams,
    MAIndicatorsQueryParams,
    SMAIndicatorsQueryParams,
    _get_type_name,
)


class _OriginWithName:
    """A stand-in generic origin exposing ``_name`` but no ``__name__``."""


class _NoOriginNoName:
    """A stand-in type hint exposing nothing recognizable."""


class TestGetTypeName:
    """Tests for the ``_get_type_name`` type-hint formatter."""

    def test_parametrized_origin_with_dunder_name(self):
        """It formats a generic whose origin exposes ``__name__``."""
        assert _get_type_name(list[int]) == "list[int]"

    def test_parametrized_origin_with_underscore_name(self):
        """It formats a generic whose origin only exposes ``_name``."""
        origin = _OriginWithName()
        origin._name = "FakeGeneric"

        class _Hint:
            pass

        hint = _Hint()
        hint.__origin__ = origin
        hint.__args__ = (int,)
        assert _get_type_name(hint) == "FakeGeneric[int]"

    def test_plain_string_hint(self):
        """It returns a string hint unchanged."""
        assert _get_type_name("close") == "close"

    def test_type_with_dunder_name(self):
        """It returns the ``__name__`` of a concrete type."""
        assert _get_type_name(int) == "int"

    def test_object_with_only_underscore_name(self):
        """It returns ``_name`` for an object lacking ``__name__``."""
        obj = _NoOriginNoName()
        obj._name = "LonelyName"
        assert _get_type_name(obj) == "LonelyName"

    def test_object_with_nothing_recognizable(self):
        """It falls back to ``str(t)`` for an unrecognized hint."""
        obj = _NoOriginNoName()
        result = _get_type_name(obj)
        assert "_NoOriginNoName object" in result


class TestChartQueryParams:
    """Tests for the ``ChartQueryParams`` base model and subclasses."""

    def test_base_default_data_is_none(self):
        """The base ``data`` field defaults to ``None``."""
        params = ChartQueryParams()
        assert params.data is None

    def test_repr_lists_parameters(self):
        """The ``__repr__`` renders the model name and a Parameters section."""
        params = EquityPriceHistoricalChartQueryParams()
        text = repr(params)
        assert "EquityPriceHistoricalChartQueryParams" in text
        assert "Parameters" in text
        assert "title" in text

    def test_doc_set_to_repr(self):
        """The instance ``__doc__`` is populated from ``__repr__``."""
        params = EquityPriceHistoricalChartQueryParams()
        assert params.__doc__ == repr(params)

    def test_subclass_field_defaults(self):
        """A populated subclass exposes its declared field defaults."""
        params = EquityPriceHistoricalChartQueryParams()
        assert params.candles is True
        assert params.volume is True
        assert params.multi_symbol is False

    def test_ma_query_params_defaults(self):
        """The moving-average query params expose their defaults."""
        params = MAIndicatorsQueryParams()
        assert params.length == 50
        assert params.offset == 0


class TestChartParams:
    """Tests for the ``ChartParams`` registry."""

    def test_known_route_maps_to_class(self):
        """A registered route maps to its query-params class."""
        assert (
            ChartParams.equity_price_historical is EquityPriceHistoricalChartQueryParams
        )

    def test_registry_supports_hasattr_lookup(self):
        """Routes are discoverable via ``hasattr`` and missing ones are not."""
        assert hasattr(ChartParams, "economy_fred_series")
        assert not hasattr(ChartParams, "does_not_exist")


class TestIndicatorsParams:
    """Tests for the ``IndicatorsParams`` aggregate model."""

    def test_default_indicators_present(self):
        """All known indicator keys are present in the default model."""
        keys = list(IndicatorsParams().model_dump().keys())
        assert "sma" in keys
        assert "macd" in keys
        assert "stoch" in keys

    def test_repr_renders_descriptions(self):
        """The ``__repr__`` renders indicator descriptions as a block."""
        text = repr(IndicatorsParams())
        assert isinstance(text, str)
        assert text.startswith("\n")
        assert len(text) > 0

    def test_nested_default_is_typed_model(self):
        """A nested default is the typed indicator-params model."""
        params = IndicatorsParams()
        assert isinstance(params.sma, SMAIndicatorsQueryParams)

    def test_invalid_indicator_key_rejected(self):
        """An unknown indicator key fails model validation."""
        with pytest.raises(ValueError, match="not a valid indicator"):
            IndicatorsParams.validate_model({"not_an_indicator": {}})

    def test_invalid_indicator_via_constructor(self):
        """Constructing with an unknown indicator raises a validation error."""
        with pytest.raises(Exception, match="not a valid indicator"):
            IndicatorsParams(bogus={"length": 1})

    def test_valid_indicator_via_constructor(self):
        """Constructing with a valid indicator key succeeds."""
        params = IndicatorsParams(sma=SMAIndicatorsQueryParams(length=10))
        assert params.sma.length == 10
