"""Tests for ``openbb_charting.core.plotly_ta.base``."""

import numpy as np
import pandas as pd
import pytest

from openbb_charting.core.plotly_ta.base import (
    Indicator,
    PltTA,
    columns_regex,
    indicator,
)


@pytest.fixture
def ohlcv_df() -> pd.DataFrame:
    """Build a deterministic OHLCV frame indexed by date."""
    rng = np.random.default_rng(11)
    idx = pd.date_range("2023-01-01", periods=60, freq="D")
    close = 100 + np.cumsum(rng.normal(0, 1, 60))
    open_ = close + rng.normal(0, 0.5, 60)
    high = np.maximum(open_, close) + np.abs(rng.normal(0, 0.5, 60))
    low = np.minimum(open_, close) - np.abs(rng.normal(0, 0.5, 60))
    volume = rng.integers(1_000_000, 5_000_000, 60)
    frame = pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )
    frame.index.name = "date"
    return frame


def _make_plugin():
    """Build a concrete ``PltTA`` subclass with indicators and a static method."""

    class SamplePlugin(PltTA):
        """A concrete plugin used by the base tests."""

        __ma_mode__ = ["sma"]
        __inchart__ = ["sma"]
        __subplots__ = ["rsi"]

        @indicator()
        def plot_sma(self, fig, df_ta, idx):
            """Bind as an indicator named after the function."""
            return fig, idx

        @indicator()
        def plot_rsi(self, fig, df_ta, idx):
            """Bind as a second indicator named after the function."""
            return fig, idx

        @staticmethod
        def sample_helper():
            """A static helper that becomes part of ``__static_methods__``."""
            return "sample"

    return SamplePlugin


class TestColumnsRegex:
    """Tests for the module-level ``columns_regex`` helper."""

    def test_matches_named_columns(self):
        """It returns the columns matching the regex name."""
        df_ta = pd.DataFrame({"SMA_20": [1], "SMA_50": [2], "RSI_14": [3]})
        assert columns_regex(df_ta, "SMA") == ["SMA_20", "SMA_50"]

    def test_no_match_returns_empty(self):
        """It returns an empty list when nothing matches."""
        df_ta = pd.DataFrame({"close": [1.0]})
        assert columns_regex(df_ta, "ZZZ") == []


class TestIndicator:
    """Tests for the ``Indicator`` wrapper class."""

    def test_init_stores_func_name_attrs(self):
        """It stores the function, name, and extra attributes."""

        def fn():
            return 1

        ind = Indicator(fn, name="myind", color="red")
        assert ind.func is fn
        assert ind.name == "myind"
        assert ind.attrs == {"color": "red"}

    def test_call_delegates_to_func(self):
        """Calling the indicator delegates to the wrapped function."""
        ind = Indicator(lambda x, y=0: x + y, name="add")
        assert ind(2, y=3) == 5


class TestIndicatorDecorator:
    """Tests for the ``indicator`` decorator factory."""

    def test_decorator_falls_back_to_func_name(self):
        """The decorator falls back to the function name when none given."""

        @indicator()
        def my_func():
            return 1

        assert isinstance(my_func, Indicator)
        assert my_func.name == "my_func"

    def test_decorator_uses_explicit_name(self):
        """An explicit ``name`` is honored (and does not raise)."""

        @indicator(name="custom_name")
        def my_func():
            return 1

        assert isinstance(my_func, Indicator)
        assert my_func.name == "custom_name"

    def test_decorator_preserves_extra_attrs(self):
        """The decorator preserves additional attributes on the indicator."""

        @indicator(subplot=True)
        def fn():
            return 1

        assert fn.attrs == {"subplot": True}


class TestPluginMeta:
    """Tests for the ``PluginMeta`` metaclass."""

    def test_collects_indicators_and_static_methods(self):
        """The metaclass collects indicators and the plugin's static methods."""
        plugin = _make_plugin()
        names = {ind.name for ind in plugin.__indicators__}
        assert {"plot_sma", "plot_rsi"} <= names
        assert "sample_helper" in plugin.__static_methods__

    def test_static_methods_do_not_leak_across_classes(self):
        """Each plugin's ``__static_methods__`` is independent (no shared-list leak)."""

        class PluginA(PltTA):
            """First plugin with its own static helper."""

            @staticmethod
            def helper_a():
                """Static helper unique to PluginA."""
                return "a"

        class PluginB(PltTA):
            """Second plugin with a different static helper."""

            @staticmethod
            def helper_b():
                """Static helper unique to PluginB."""
                return "b"

        assert "helper_a" in PluginA.__static_methods__
        assert "helper_a" not in PluginB.__static_methods__
        assert "helper_b" in PluginB.__static_methods__
        assert "helper_b" not in PluginA.__static_methods__

    def test_collects_class_attribute_lists(self):
        """The metaclass aggregates ma_mode, inchart, and subplots."""
        plugin = _make_plugin()
        assert "sma" in plugin.__ma_mode__
        assert "sma" in plugin.__inchart__
        assert "rsi" in plugin.__subplots__

    def test_iter_yields_indicators(self):
        """Iterating the class yields its indicators."""
        plugin = _make_plugin()
        assert list(iter(plugin)) == plugin.__indicators__

    def test_indicator_as_static_method_raises(self):
        """An indicator declared as a static method raises TypeError."""
        with pytest.raises(TypeError, match="can't be a static method"):

            class BadPlugin(PltTA):
                """Declares an indicator as a static method, which is illegal."""

                bad = staticmethod(Indicator(lambda self: None, name="bad"))

    def test_subclass_overrides_parent_indicator(self):
        """A subclass redefining an indicator removes the parent's copy."""
        parent = _make_plugin()

        class ChildPlugin(parent):
            """Overrides an inherited indicator with a plain attribute."""

            plot_sma = "not-an-indicator"

        child_names = {ind.name for ind in ChildPlugin.__indicators__}
        assert "plot_sma" not in child_names
        assert "plot_rsi" in child_names


class TestPltTA:
    """Tests for the ``PltTA`` base class."""

    def test_cannot_instantiate_abstract_base(self):
        """Instantiating ``PltTA`` directly raises TypeError."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            PltTA()

    def test_new_binds_indicators(self):
        """A concrete instance exposes its indicators as callables."""
        plugin = _make_plugin()
        inst = plugin()
        assert callable(inst.plot_sma)
        assert callable(inst.plot_rsi)

    def test_new_binds_custom_named_indicator(self):
        """An indicator whose name differs from its attribute is bound on the instance."""

        class CustomNamePlugin(PltTA):
            """A plugin with an indicator registered under a custom name."""

            @indicator(name="aliased")
            def plot_thing(self, fig, df_ta, idx):
                """Indicator registered under the name ``aliased``."""
                return fig, idx

        inst = CustomNamePlugin()
        assert callable(inst.aliased)

    def test_ma_mode_property_and_setter(self):
        """The ``ma_mode`` property returns a unique list and can be set."""
        inst = _make_plugin()()
        assert "sma" in inst.ma_mode
        inst.ma_mode = ["ema", "ema", "wma"]
        assert set(inst.ma_mode) == {"ema", "wma"}

    def test_iter_yields_instance_indicators(self):
        """Iterating an instance yields its indicators."""
        inst = _make_plugin()()
        assert list(iter(inst)) == inst.__indicators__

    def test_add_plugins_merges_indicators_and_attrs(self):
        """``add_plugins`` merges another plugin's indicators and attrs."""

        class OtherPlugin(PltTA):
            """A second plugin providing an extra indicator and subplot entry."""

            __subplots__ = ["macd"]

            @indicator()
            def plot_macd(self, fig, df_ta, idx):
                """Extra indicator added via add_plugins."""
                return fig, idx

        base_inst = _make_plugin()()
        before = len(base_inst.__indicators__)
        base_inst.add_plugins([OtherPlugin])
        assert len(base_inst.__indicators__) == before + 1
        assert callable(base_inst.plot_macd)
        assert "macd" in base_inst.__subplots__

    def test_add_plugins_binds_static_methods(self):
        """``add_plugins`` binds a plugin's static methods onto the instance."""

        class StaticPlugin(PltTA):
            """A plugin contributing a static helper."""

            @staticmethod
            def extra_helper():
                """A static helper to be bound onto the aggregating instance."""
                return "extra"

        base_inst = _make_plugin()()
        assert not hasattr(base_inst, "extra_helper")
        base_inst.add_plugins([StaticPlugin])
        assert base_inst.extra_helper() == "extra"

    def test_add_plugins_skips_existing_indicator(self):
        """``add_plugins`` does not re-add an indicator already on the instance."""

        class DuplicatePlugin(PltTA):
            """A plugin whose indicator name already exists on the target."""

            @indicator()
            def plot_sma(self, fig, df_ta, idx):
                """Indicator with a name shared by the base plugin."""
                return fig, idx

        base_inst = _make_plugin()()
        before = len(base_inst.__indicators__)
        base_inst.add_plugins([DuplicatePlugin])
        assert len(base_inst.__indicators__) == before

    def test_remove_plugins_removes_indicators_and_static_methods(self):
        """``remove_plugins`` removes a plugin's indicators and bound static methods."""

        class RemovablePlugin(PltTA):
            """A plugin whose indicator and static helper get removed."""

            @indicator()
            def plot_temp(self, fig, df_ta, idx):
                """Indicator that will be removed."""
                return fig, idx

            @staticmethod
            def temp_helper():
                """Static helper that will be removed."""
                return "temp"

        base_inst = _make_plugin()()
        base_inst.add_plugins([RemovablePlugin])
        assert hasattr(base_inst, "plot_temp")
        assert base_inst.temp_helper() == "temp"

        base_inst.remove_plugins([RemovablePlugin])
        assert not hasattr(base_inst, "plot_temp")
        assert "temp_helper" not in base_inst.__dict__

    def test_get_float_precision_two_decimals(self, ohlcv_df):
        """A price above 1.10 yields a two-decimal precision format."""
        inst = _make_plugin()()
        inst.df_stock = ohlcv_df
        inst.close_column = "close"
        assert inst.get_float_precision() == ",.2f"

    def test_get_float_precision_six_decimals(self, ohlcv_df):
        """A long low-priced value yields a six-decimal precision format."""
        inst = _make_plugin()()
        frame = ohlcv_df.copy()
        frame["close"] = 0.123456789
        inst.df_stock = frame
        inst.close_column = "close"
        assert inst.get_float_precision() == ".6f"

    def test_get_float_precision_empty_format(self, ohlcv_df):
        """A short low-priced value yields an empty precision format."""
        inst = _make_plugin()()
        frame = ohlcv_df.copy()
        frame["close"] = 0.5
        inst.df_stock = frame
        inst.close_column = "close"
        assert inst.get_float_precision() == ""
