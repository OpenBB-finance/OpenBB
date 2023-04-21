from typing import Any, Callable, Dict, Iterator, List, Optional, Type

import pandas as pd

from .data_classes import ChartIndicators, TAIndicator


def columns_regex(df_ta: pd.DataFrame, name: str) -> List[str]:
    """Return columns that match regex name"""
    column_name = df_ta.filter(regex=rf"{name}(?=[^\d]|$)").columns.tolist()

    return column_name


class Indicator:
    """Class for technical indicator."""

    def __init__(
        self,
        func: Callable,
        name: str = "",
        **attrs: Any,
    ) -> None:
        self.func = func
        self.name = name
        self.attrs = attrs

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)


class PluginMeta(type):
    """Metaclass for all Plotly plugins."""

    __indicators__: List[Indicator] = []
    __static_methods__: list = []
    __ma_mode__: List[str] = []
    __inchart__: List[str] = []
    __subplots__: List[str] = []

    def __new__(mcs: Type["PluginMeta"], *args: Any, **kwargs: Any) -> "PluginMeta":
        name, bases, attrs = args
        indicators: Dict[str, Indicator] = {}
        cls_attrs: Dict[str, list] = {
            "__ma_mode__": [],
            "__inchart__": [],
            "__subplots__": [],
        }
        new_cls = super().__new__(mcs, name, bases, attrs, **kwargs)
        for base in reversed(new_cls.__mro__):
            for elem, value in base.__dict__.items():
                if elem in indicators:
                    del indicators[elem]

                is_static_method = isinstance(value, staticmethod)
                if is_static_method:
                    value = value.__func__
                if isinstance(value, Indicator):
                    if is_static_method:
                        raise TypeError(
                            f"Indicator {value.name} can't be a static method"
                        )
                    indicators[value.name] = value
                elif is_static_method and elem not in new_cls.__static_methods__:
                    new_cls.__static_methods__.append(elem)

                if elem in ["__ma_mode__", "__inchart__", "__subplots__"]:
                    cls_attrs[elem].extend(value)

        new_cls.__indicators__ = list(indicators.values())
        new_cls.__static_methods__ = list(set(new_cls.__static_methods__))
        new_cls.__ma_mode__ = list(set(cls_attrs["__ma_mode__"]))
        new_cls.__inchart__ = list(set(cls_attrs["__inchart__"]))
        new_cls.__subplots__ = list(set(cls_attrs["__subplots__"]))

        return new_cls

    def __iter__(cls: Type["PluginMeta"]) -> Iterator[Indicator]:  # type: ignore
        return iter(cls.__indicators__)

    # pylint: disable=unused-argument
    def __init__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class PltTA(metaclass=PluginMeta):
    """The base class that all Plotly plugins must inherit from."""

    indicators: ChartIndicators
    intraday: bool = False
    df_stock: pd.DataFrame
    df_ta: pd.DataFrame
    df_fib: pd.DataFrame
    close_column: Optional[str] = "Close"
    params: Dict[str, TAIndicator] = {}
    inchart_colors: List[str] = []
    show_volume: bool = True

    __static_methods__: list = []
    __indicators__: List[Indicator] = []
    __ma_mode__: List[str] = []
    __inchart__: List[str] = []
    __subplots__: List[str] = []

    # pylint: disable=unused-argument
    def __new__(cls, *args: Any, **kwargs: Any) -> "PltTA":
        if cls is PltTA:
            raise TypeError("Can't instantiate abstract class Plugin directly")
        self = super().__new__(cls)

        static_methods = cls.__static_methods__
        indicators = cls.__indicators__

        for item in indicators:
            # we make sure that the indicator is bound to the instance
            if not hasattr(self, item.name):
                setattr(self, item.name, item.func.__get__(self, cls))

        for static_method in static_methods:
            if not hasattr(self, static_method):
                setattr(self, static_method, staticmethod(getattr(self, static_method)))

        for attr, value in cls.__dict__.items():
            if attr in [
                "__ma_mode__",
                "__inchart__",
                "__subplots__",
            ] and value not in getattr(self, attr):
                getattr(self, attr).extend(value)

        return self

    @property
    def ma_mode(self) -> List[str]:
        return list(set(self.__ma_mode__))

    @ma_mode.setter
    def ma_mode(self, value: List[str]):
        self.__ma_mode__ = value

    def add_plugins(self, plugins: List["PltTA"]) -> None:
        """Add plugins to current instance"""
        for plugin in plugins:
            for item in plugin.__indicators__:
                # pylint: disable=unnecessary-dunder-call
                if not hasattr(self, item.name):
                    setattr(self, item.name, item.func.__get__(self, type(self)))
                    self.__indicators__.append(item)

            for static_method in plugin.__static_methods__:
                if not hasattr(self, static_method):
                    setattr(
                        self, static_method, staticmethod(getattr(self, static_method))
                    )
            for attr, value in plugin.__dict__.items():
                if attr in [
                    "__ma_mode__",
                    "__inchart__",
                    "__subplots__",
                ] and value not in getattr(self, attr):
                    getattr(self, attr).extend(value)

    def remove_plugins(self, plugins: List["PltTA"]) -> None:
        """Remove plugins from current instance"""
        for plugin in plugins:
            for item in plugin.__indicators__:
                delattr(self, item.name)
                self.__indicators__.remove(item)

            for static_method in plugin.__static_methods__:
                delattr(self, static_method)

    def __iter__(self) -> Iterator[Indicator]:
        return iter(self.__indicators__)

    def get_float_precision(self) -> str:
        """Returns f-string precision format"""
        price = self.df_stock[self.close_column].tail(1).values[0]
        float_precision = (
            ",.2f" if price > 1.10 else "" if len(str(price)) < 8 else ".6f"
        )
        return float_precision


def indicator(
    name: str = "",
    **attrs: Any,
) -> Callable:
    """Decorator for adding indicators to a plugin class."""
    attrs["name"] = name

    def decorator(func: Callable) -> Indicator:
        if not attrs.pop("name", ""):
            name = func.__name__

        return Indicator(func, name, **attrs)

    return decorator
