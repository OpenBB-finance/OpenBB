"""Dataclasses for the charting extension."""

# pylint: disable=C0302,R0915,R0914,R0913,R0903,R0904

import sys
import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Tuple, Union

if TYPE_CHECKING:
    from pandas import DataFrame, Series

# pylint: disable=E1123
datacls_kwargs = {"slots": True} if sys.version_info >= (3, 10) else {}


def columns_regex(df_ta: "DataFrame", name: str) -> List[str]:
    """Return columns that match regex name."""
    column_name = df_ta.filter(regex=rf"{name}(?=[^\d]|$)").columns.tolist()

    return column_name


@dataclass(**datacls_kwargs)
class Arguments:
    """Arguments for technical analysis indicators."""

    label: str
    values: Any

    def __post_init__(self):
        """Post init."""
        if isinstance(self.values, list) and len(self.values) == 1:
            self.values = self.values[0]


@dataclass(**datacls_kwargs)
class TAIndicator:
    """Technical analysis indicator."""

    name: Literal[
        "ad",
        "adosc",
        "adx",
        "aroon",
        "atr",
        "cci",
        "donchian",
        "fisher",
        "kc",
        "obv",
        "stoch",
        "vwap",
        "fib",
        "srlines",
        "clenow",
        "demark",
        "ichimoku",
        "sma",
        "ema",
        "wma",
        "hma",
        "zlma",
        "rma",
    ]
    args: List[Arguments]

    def __iter__(self):
        """Return iterator."""
        return iter(self.args)

    def get_args(self, label: str) -> Union[Arguments, None]:
        """Return arguments by label."""
        output = None
        for opt in self.args:
            if opt.label == label:
                output = opt
        return output

    def get_argument_values(self, label: str) -> Union[List[Any], Any]:
        """Return arguments values by label."""
        output = []
        options = self.get_args(label)
        if options is not None:
            output = options.values
        return output


@dataclass(**datacls_kwargs)
class ChartIndicators:
    """Chart technical analysis indicators."""

    indicators: Optional[List[TAIndicator]] = None

    def get_indicator(self, name: str) -> Union[TAIndicator, None]:
        """Return indicator with given name."""
        output = None
        for indicator in self.indicators:  # type: ignore
            if indicator.name == name:
                output = indicator
        return output

    def get_indicator_args(self, name: str, label: str) -> Union[Arguments, None]:
        """Return argument values for given indicator and label."""
        output = None
        indicator = self.get_indicator(name)
        if indicator is not None:
            output = indicator.get_args(label)
            if output is not None:
                output = output.values
        return output

    def get_indicators(self) -> Optional[List[TAIndicator]]:
        """Return active indicators and their arguments."""
        return self.indicators

    def get_params(self) -> Dict[str, TAIndicator]:
        """Return dictionary of active indicators and their arguments."""
        output = {}
        if self.indicators:
            output = {str(indicator.name): indicator for indicator in self.indicators}
        return output

    def get_active_ids(self) -> List[str]:
        """Return list of names of active indicators."""
        active_ids = []
        if self.indicators:
            active_ids = [str(indicator.name) for indicator in self.indicators]
        return active_ids

    def get_arg_names(self, name: str) -> List[str]:
        """Return list of argument labels for given indicator."""
        output = []
        indicator = self.get_indicator(name)
        if indicator is not None:
            for opt in indicator.args:
                output.append(opt.label)
        return output

    def get_options_dict(self, name: str) -> Dict[str, Optional[Arguments]]:
        """Return dictionary of argument labels and values for given indicator."""
        output = None
        options = self.get_arg_names(name)
        if options:
            output = {}
            for opt in options:
                output[opt] = self.get_indicator_args(name, opt)

        return output

    @staticmethod
    def get_available_indicators() -> Tuple[str, ...]:
        """Return tuple of available indicators."""
        return tuple(
            TAIndicator.__annotations__["name"].__args__  # pylint: disable=E1101
        )

    @classmethod
    def from_dict(
        cls, indicators: Dict[str, Dict[str, List[Dict[str, Any]]]]
    ) -> "ChartIndicators":
        """Return ChartIndicators from dictionary.

        Example
        -------
        ChartIndicators.from_dict(
            {
                "ad": {
                    "args": [
                        {
                            "label": "AD_LABEL",
                            "values": [1, 2, 3],
                        }
                    ]
                }
            }
        )
        """
        return cls(
            indicators=[
                TAIndicator(
                    name=name,  # type: ignore[arg-type]
                    args=[
                        Arguments(label=label, values=values)
                        for label, values in args.items()
                    ],
                )
                for name, args in indicators.items()
            ]
        )

    def to_dataframe(
        self, df_ta: "DataFrame", ma_mode: Optional[List[str]] = None
    ) -> "DataFrame":
        """Calculate technical analysis indicators and return dataframe."""
        output = df_ta.copy()
        if not output.empty and self.indicators:
            try:
                output = TA_Data(output, self, ma_mode).to_dataframe()
            except Exception as err:
                warnings.warn(str(err))

        return output

    def get_indicator_data(self, df_ta: "DataFrame", indicator: TAIndicator, **kwargs):
        """Return dataframe with technical analysis indicators."""
        output = None
        if self.indicators:
            try:
                output = TA_Data(df_ta, self).get_indicator_data(indicator, **kwargs)
            except Exception as err:
                warnings.warn(str(err))

        return output

    def remove_indicator(self, name: str) -> None:
        """Remove indicator from active indicators."""
        if self.indicators:
            for indicator in self.indicators:
                if indicator.name == name:
                    self.indicators.remove(indicator)


class TA_DataException(Exception):
    """Exception for TA_Data."""


class TA_Data:
    """
    Process technical analysis data.

    Parameters
    ----------
    df_ta : DataFrame
        Dataframe with OHLCV data
    indicators : Union[ChartIndicators, Dict[str, Dict[str, Any]]]
        ChartIndicators object or dictionary with indicators and arguments
        Example:
            dict(
                sma=dict(length=[20, 50, 100]),
                adx=dict(length=14),
                macd=dict(fast=12, slow=26, signal=9),
                rsi=dict(length=14),
            )

    Methods
    -------
    to_dataframe()
        Return dataframe with technical analysis indicators
    get_indicator_data(indicator: TAIndicator, **kwargs)
        Return dataframe given indicator and arguments
    """

    def __init__(
        self,
        df_ta: Union["DataFrame", "Series"],
        indicators: Union[ChartIndicators, Dict[str, Dict[str, Any]]],
        ma_mode: Optional[List[str]] = None,
    ):
        """Initialize."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame, Series  # noqa
        from openbb_charting.core.plotly_ta.ta_helpers import check_columns  # noqa

        if isinstance(df_ta, Series):
            df_ta = df_ta.to_frame()

        if not isinstance(indicators, ChartIndicators):
            indicators = ChartIndicators.from_dict(indicators)

        self.df_ta: DataFrame = df_ta
        self.indicators: ChartIndicators = indicators
        self.ma_mode: List[str] = ma_mode or ["sma", "ema", "wma", "hma", "zlma", "rma"]
        self.close_col = check_columns(df_ta)
        if self.close_col is None:
            raise ValueError("No close column found in dataframe")

        self.columns: Dict[str, List[str]] = {
            "ad": ["high", "low", self.close_col, "volume"],
            "adosc": ["high", "low", self.close_col, "volume"],
            "adx": ["high", "low", self.close_col],
            "aroon": ["high", "low"],
            "atr": ["high", "low", self.close_col],
            "cci": ["high", "low", self.close_col],
            "donchian": ["high", "low"],
            "fisher": ["high", "low"],
            "kc": ["high", "low", self.close_col],
            "obv": [self.close_col, "volume"],
            "stoch": ["high", "low", self.close_col],
            "vwap": ["high", "low", self.close_col, "volume"],
        }

        self.has_volume = "volume" in df_ta.columns and bool(df_ta["volume"].sum() > 0)

    def get_indicator_data(self, indicator: TAIndicator, **args) -> "DataFrame":
        """
        Return dataframe with indicator data.

        Parameters
        ----------
        indicator : TAIndicator
            TAIndicator object
        args : dict
            Arguments for given indicator

        Return
        -------
        DataFrame
            Dataframe with indicator data
        """
        # pylint: disable=import-outside-toplevel
        import pandas_ta as ta
        from pandas import DataFrame

        output = None
        if indicator and indicator.name in self.ma_mode:
            if isinstance(indicator.get_argument_values("length"), list):
                df_ta = DataFrame()

                for length in indicator.get_argument_values("length"):
                    df_ma = getattr(ta, indicator.name)(
                        self.df_ta[self.close_col], length=length
                    )
                    df_ta.insert(0, f"{indicator.name.upper()}_{length}", df_ma)

                output = df_ta

            else:
                output = getattr(ta, indicator.name)(
                    self.df_ta[self.close_col],
                    length=indicator.get_argument_values("length"),
                )
                if indicator.name == "zlma" and output is not None:
                    output.name = output.name.replace("ZL_EMA", "ZLMA")

        elif indicator.name == "vwap":
            ta_columns = self.columns[indicator.name]
            ta_columns = [self.df_ta[col] for col in ta_columns]  # type: ignore

            output = getattr(ta, indicator.name)(
                *ta_columns,
            )
        elif indicator.name in self.columns:
            ta_columns = self.columns[indicator.name]
            ta_columns = [self.df_ta[col] for col in ta_columns]  # type: ignore

            if indicator.get_argument_values("use_open") is True:
                ta_columns.append(self.df_ta["open"])

            output = getattr(ta, indicator.name)(*ta_columns, **args)
        else:
            output = getattr(ta, indicator.name)(self.df_ta[self.close_col], **args)

        # Drop NaN values from output and return None if empty
        if output is not None:
            output.dropna(inplace=True)
            if output.empty:
                output = None

        return output

    def to_dataframe(self) -> "DataFrame":
        """Return dataframe with all indicators."""
        active_indicators = self.indicators.get_indicators()

        if not active_indicators:
            return None

        output = self.df_ta
        for indicator in active_indicators:
            if (
                indicator.name in self.columns
                and "volume" in self.columns[indicator.name]
                and not self.has_volume
            ):
                continue
            if indicator.name in ["fib", "srlines", "clenow", "demark", "ichimoku"]:
                continue
            try:
                indicator_data = self.get_indicator_data(
                    indicator,
                    **self.indicators.get_options_dict(indicator.name) or {},
                )
            except Exception as e:
                indicator_data = None
                raise TA_DataException(
                    f"Error processing indicator {indicator.name}: {e}"
                ) from e

            if indicator_data is not None:
                output = output.join(indicator_data).infer_objects(copy=False)
                numeric_cols = output.select_dtypes(include=["number"]).columns
                output[numeric_cols] = output[numeric_cols].interpolate("linear")

        return output
