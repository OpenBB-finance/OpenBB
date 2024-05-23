"""Relative Rotation Model."""

# pylint: disable=too-many-arguments, too-many-instance-attributes, protected-access
# pylint: disable=too-many-locals, too-few-public-methods, unused-argument

import contextlib
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import numpy as np
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.utils import basemodel_to_df, convert_to_basemodel, df_to_basemodel
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pandas import DataFrame, Series, to_datetime
from pydantic import Field, field_validator


def absolute_maximum_scale(data: Series) -> Series:
    """Absolute Maximum Scale Normaliztion Method."""
    return data / data.abs().max()


def min_max_scaling(data: Series) -> Series:
    """Min/Max ScalingNormalization Method."""
    return (data - data.min()) / (data.max() - data.min())


def z_score_standardization(data: Series) -> Series:
    """Z-Score Standardization Method."""
    return (data - data.mean()) / data.std()


def normalize(data: DataFrame, method: Literal["z", "m", "a"] = "z") -> DataFrame:
    """
    Normalize a Pandas DataFrame based on method.

    Parameters
    ----------
    data: DataFrame
        Pandas DataFrame with any number of columns to be normalized.
    method: Literal["z", "m", "a"]
        Normalization method.
            z: Z-Score Standardization
            m: Min/Max Scaling
            a: Absolute Maximum Scale

    Returns
    -------
    DataFrame
        Normalized DataFrame.
    """
    methods = {
        "z": z_score_standardization,
        "m": min_max_scaling,
        "a": absolute_maximum_scale,
    }

    df = data.copy()

    for col in df.columns:
        df.loc[:, col] = methods[f"{method}"](df.loc[:, col])

    return df


def standard_deviation(
    data: DataFrame,
    window: int = 21,
    trading_periods: int = 252,
) -> DataFrame:
    """
    Measures how widely returns are dispersed from the average return.

    It is the most common (and biased) estimator of volatility.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices.
    window : int [default: 21]
        Length of window to calculate over.
    trading_periods : Optional[int] [default: 252]
        Number of trading periods in a year.

    Returns
    -------
    pd.DataFrame : results
        Dataframe with results.
    """
    data = data.copy()
    results = DataFrame()
    if window < 2:
        window = 21

    for col in data.columns.tolist():
        log_return = (data[col] / data[col].shift(1)).apply(np.log)

        result = log_return.rolling(window=window, center=False).std() * np.sqrt(
            trading_periods
        )
        results[col] = result

    return results.dropna()


def calculate_momentum(
    data: Series, long_period: int = 252, short_period: int = 21
) -> Series:
    """
    Momentum is calculated as the log trailing 12-month return minus trailing one-month return.

    Higher values indicate larger, positive momentum exposure.

    Momentum = ln(1 + r12) - ln(1 + r1)

    Parameters
    ----------
    data: Series
        Time series data to calculate the momentum for.
    long_period: Optional[int]
        Long period to base the calculation on. Default is one standard trading year.
    short_period: Optional[int]
        Short period to subtract from the long period. Default is one trading month.

    Returns
    -------
    Series
        Pandas Series with the calculated momentum.
    """
    df = data.copy()
    epsilon = 1e-10
    momentum_long = np.log(1 + df.pct_change(long_period) + epsilon)
    momentum_short = np.log(1 + df.pct_change(short_period) + epsilon)
    data = momentum_long - momentum_short  # type: ignore

    return data


def get_momentum(
    data: DataFrame, long_period: int = 252, short_period: int = 21
) -> DataFrame:
    """
    Calculate the Relative-Strength Momentum Indicator.

    Takes the Relative Strength Ratio as the input.

    Parameters
    ----------
    data: DataFrame
        Indexed time series data formatted with each column representing a ticker.
    long_period: Optional[int]
        Long period to base the calculation on. Default is one standard trading year.
    short_period: Optional[int]
        Short period to subtract from the long period. Default is one trading month.

    Returns
    -------
    DataFrame
        Pandas DataFrame with the calculated historical momentum factor exposure score.
    """
    df = data.copy()
    rs_momentum = DataFrame()
    for ticker in df.columns.to_list():
        rs_momentum.loc[:, ticker] = calculate_momentum(
            df.loc[:, ticker], long_period, short_period
        )  # type: ignore

    return rs_momentum


def calculate_relative_strength_ratio(
    symbols_data: DataFrame,
    benchmark_data: DataFrame,
) -> DataFrame:
    """Calculate the Relative Strength Ratio for each ticker (column) in a DataFrame against the benchmark.

    Symbols data and benchmark data should have the same index,
    and each column should represent a ticker.

    Parameters
    ----------
    symbols_data: DataFrame
        Pandas DataFrame with the symbols data to compare against the benchmark.
    benchmark_data: DataFrame
        Pandas DataFrame with the benchmark data.

    Returns
    -------
    DataFrame
        Pandas DataFrame with the calculated relative strength
        ratio for each ticker joined with the benchmark values.
    """
    return (
        symbols_data.div(benchmark_data.iloc[:, 0], axis=0)
        .multiply(100)
        .join(benchmark_data.iloc[:, 0])
        .dropna()
    )


def process_data(
    symbols_data: DataFrame,
    benchmark_data: DataFrame,
    long_period: int = 252,
    short_period: int = 21,
    normalize_method: Literal["z", "m", "a"] = "z",
) -> Tuple[DataFrame, DataFrame]:
    """Process the raw data into normalized indicator values.

    Parameters
    ----------
    symbols_data: DataFrame
        Indexed time series data formatted with each column representing a ticker.
    benchmark_data: DataFrame
        Indexed time series data of the benchmark symbol.
    long_period: Optional[int]
        Long period to base the calculation on. Default is one standard trading year.
    short_period: Optional[int]
        Short period to subtract from the long period. Default is one trading month.
    normalize_method: Literal["z", "m", "a"]

    Returns
    -------
    Tuple[DataFrame, DataFrame]
        Tuple of Pandas DataFrames with the normalized ratio and momentum indicator values.
    """
    ratio_data = calculate_relative_strength_ratio(symbols_data, benchmark_data)
    momentum_data = get_momentum(ratio_data, long_period, short_period)
    normalized_ratio = normalize(ratio_data, normalize_method)
    normalized_momentum = normalize(momentum_data, normalize_method)

    return normalized_ratio, normalized_momentum


class RelativeRotation:
    """Relative Rotation Class."""

    def __init__(
        self,
        data: Union[List[Data], DataFrame],
        benchmark: str,
        study: Optional[Literal["price", "volume", "volatility"]] = "price",
        long_period: Optional[int] = 252,
        short_period: Optional[int] = 21,
        window: Optional[int] = 21,
        trading_periods: Optional[int] = 252,
    ):
        """Initialize the class."""
        benchmark = benchmark.upper()
        df = DataFrame()

        target_col = "volume" if study == "volume" else "close"

        if isinstance(data, OBBject):
            data = data.results  # type: ignore

        if isinstance(data, List) and (
            all(isinstance(d, Data) for d in data)
            or all(isinstance(d, dict) for d in data)
        ):
            with contextlib.suppress(Exception):
                df = basemodel_to_df(convert_to_basemodel(data), index="date")

        if isinstance(data, DataFrame) and not df.empty:
            df = data.copy()
            if "date" in df.columns:
                df.set_index("date", inplace=True)

        if df.empty:
            raise ValueError(
                "Data must be a list of Data objects or a DataFrame with a 'date' column."
            )

        if "symbol" in df.columns:
            df = df.pivot(columns="symbol", values=target_col)

        if benchmark not in df.columns:
            raise RuntimeError("The benchmark symbol was not found in the data.")

        benchmark_data = df.pop(benchmark).to_frame()
        symbols_data = df

        if len(symbols_data) <= 252 and study in ["price", "volume"]:  # type: ignore
            raise ValueError(
                "Supplied data must be daily intervals and have more than one year of back data to calculate"
                " the most recent day in the time series."
            )

        if study == "volatility" and len(symbols_data) <= 504:  # type: ignore
            raise ValueError(
                "Supplied data must be daily intervals and have more than two years of back data to calculate"
                " the most recent day in the time series as a volatility study."
            )
        self.symbols = df.columns.to_list()
        self.benchmark = benchmark
        self.study = study
        self.long_period = long_period
        self.short_period = short_period
        self.window = window
        self.trading_periods = trading_periods
        self.symbols_data = symbols_data  # type: ignore
        self.benchmark_data = benchmark_data  # type: ignore
        self._process_data()  # type: ignore
        self.symbols_data = df_to_basemodel(self.symbols_data.reset_index())  # type: ignore
        self.benchmark_data = df_to_basemodel(self.benchmark_data.reset_index())  # type: ignore

    def _process_data(self):
        """Process the data."""
        if self.study == "volatility":
            self.symbols_data = standard_deviation(
                self.symbols_data,  # type: ignore
                window=self.window,  # type: ignore
                trading_periods=self.trading_periods,  # type: ignore
            )
            self.benchmark_data = standard_deviation(
                self.benchmark_data,  # type: ignore
                window=self.window,  # type: ignore
                trading_periods=self.trading_periods,  # type: ignore
            )
        ratios, momentum = process_data(
            self.symbols_data,  # type: ignore
            self.benchmark_data,  # type: ignore
            long_period=self.long_period,  # type: ignore
            short_period=self.short_period,  # type: ignore
        )
        # Re-index rs_ratios using the new index
        index_after_dropping_nans = momentum.dropna().index
        ratios = ratios.reindex(index_after_dropping_nans)
        self.rs_ratios = df_to_basemodel(ratios.reset_index())
        self.rs_momentum = df_to_basemodel(momentum.dropna().reset_index())
        self.end_date = to_datetime(ratios.index[-1]).strftime("%Y-%m-%d")
        self.start_date = to_datetime(ratios.index[0]).strftime("%Y-%m-%d")
        return self


def _get_type_name(t):
    """Get the type name of a type hint."""
    if hasattr(t, "__origin__"):
        if hasattr(t.__origin__, "__name__"):
            return f"{t.__origin__.__name__}[{', '.join([_get_type_name(arg) for arg in t.__args__])}]"
        if hasattr(t.__origin__, "_name"):
            return f"{t.__origin__._name}[{', '.join([_get_type_name(arg) for arg in t.__args__])}]"
    if isinstance(t, str):
        return t
    if hasattr(t, "__name__"):
        return t.__name__
    if hasattr(t, "_name"):
        return t._name
    return str(t)


class RelativeRotationQueryParams(QueryParams):
    """Relative Rotation Query Parameters."""

    data: List[Data] = Field(
        description="The data to be used for the relative rotation calculations."
        + " This should be the multi-symbol output from the"
        + " 'equity.price.historical' endpoint, or similar, at a daily interval."
        + " Or a pivot table with the 'date' column as the index, the symbols as the columns,"
        + " and the 'study' as the values."
        + " It is recommended to use the 'equity.price.historical' endpoint to get the data,"
        + " and feed the results as-is."
    )
    benchmark: str = Field(description="The symbol to be used as the benchmark.")
    study: Literal["price", "volume", "volatility"] = Field(
        default="price",
        description="The data point for the calculations."
        + " If 'price', the closing price will be used."
        + " If 'volatility', the standard deviation of the closing price will be used."
        + " If 'data' is supplied as a pivot table,"
        + " the 'study' will assume the values are the closing price and 'volume' will be ignored.",
    )
    long_period: Optional[int] = Field(
        default=252,
        description="The length of the long period for momentum calculation, by default is 252."
        + " Adjust this value, to 365, when supplying assets such as crypto.",
    )
    short_period: Optional[int] = Field(
        default=21,
        description="The length of the short period for momentum calculation, by default is 21."
        + " Adjust this value, to 30, when supplying assets such as crypto.",
    )
    window: Optional[int] = Field(
        default=21,
        description="The length of window for the standard deviation calculation, by default is 21."
        + " Adjust this value, to 30, when supplying assets such as crypto.",
    )
    trading_periods: Optional[int] = Field(
        default=252,
        description="The number of trading periods per year,"
        + " for the standard deviation calculation, by default is 252."
        + " Adjust this value, to 365, when supplying assets such as crypto.",
    )
    chart_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional parameters to pass when `chart=True` and the `openbb-charting` extension is installed."
        + " Parameters can be passed again to redraw the chart using the charting.to_chart() method of the response."
        + "\n"
        + "\n            ChartParams"
        + "\n            -----------"
        + "\n            date: Optional[str]"
        + "\n                A target end date within the data, by default is the last date in the data."
        + "\n            show_tails: bool"
        + "\n                Show the tails on the chart, by default is True."
        + "\n            tail_periods: Optional[int]"
        + "\n                Number of periods to show in the tails, by default is 16."
        + "\n            tail_interval: Literal['day', 'week', 'month']"
        + "\n                Interval to show the tails, by default is 'week'."
        + "\n            title: Optional[str]"
        + "\n                Title of the chart.",
    )

    @field_validator("benchmark", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v):
        """Convert the benchmark symbol to uppercase."""
        return v.upper()

    @field_validator("data", mode="before", check_fields=False)
    @classmethod
    def convert_data(cls, v):
        """Validate the data format."""
        if isinstance(v, OBBject):
            return v.results
        if isinstance(v, Data):
            return v
        if isinstance(v, (list, dict)):
            return convert_to_basemodel(v)
        if isinstance(v, DataFrame):
            return df_to_basemodel(v.reset_index())
        return v

    def __init__(self, **data):
        """Initialize the class."""
        super().__init__(**data)
        fields = self.__class__.model_fields
        doc_str = (
            "\n"
            + self.__class__.__name__
            + "\n\n"
            + "    Parameters\n"
            + "    ----------\n"
            + "\n".join(
                [
                    f"    {k} : {_get_type_name(v.annotation)}\n        {v.description}"
                    for k, v in fields.items()
                ]
            )
            + "\n"
        )
        self.__doc__ = doc_str


class RelativeRotationData(Data):
    """Relative Rotation Data Model."""

    symbols: List[str] = Field(
        description="The symbols that are being compared against the benchmark."
    )
    benchmark: str = Field(description="The benchmark symbol, as entered by the user.")
    study: Literal["price", "volume", "volatility"] = Field(
        description="The data point for the study, as entered by the user."
    )
    long_period: int = Field(
        description="The length of the long period for momentum calculation,"
        + " as entered by the user."
    )
    short_period: int = Field(
        description="The length of the short period for momentum calculation,"
        + " as entered by the user."
    )
    window: int = Field(
        description="The length of window for the standard deviation calculation,"
        + " as entered by the user.",
    )
    trading_periods: int = Field(
        description="The number of trading periods per year,"
        + " for the standard deviation calculation, as entered by the user."
    )
    start_date: str = Field(
        description="The start date of the data after adjusting"
        + " the length of the data for the calculations."
    )
    end_date: str = Field(description="The end date of the data.")
    symbols_data: List[Data] = Field(
        description="The data representing the selected 'study' for each symbol."
    )
    benchmark_data: List[Data] = Field(
        description="The data representing the selected 'study' for the benchmark."
    )
    rs_ratios: List[Data] = Field(
        description="The normalized relative strength ratios data."
    )
    rs_momentum: List[Data] = Field(
        description="The normalized relative strength momentum data."
    )

    def __init__(self, **data):
        """Initialize the class."""
        super().__init__(**data)
        fields = self.__class__.model_fields
        doc_str = (
            "\n"
            + self.__class__.__name__
            + "\n\n"
            + "    Attributes\n"
            + "    ----------\n"
            + "\n".join(
                [
                    f"    {k} : {_get_type_name(v.annotation)}\n        {v.description}"
                    for k, v in fields.items()
                ]
            )
            + "\n"
        )
        self.__doc__ = doc_str


class RelativeRotationFetcher(
    Fetcher[RelativeRotationQueryParams, RelativeRotationData]
):
    """Relative Rotation Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> RelativeRotationQueryParams:
        """Transform the query parameters."""
        return RelativeRotationQueryParams.model_validate(**params)

    @staticmethod
    def extract_data(
        query: RelativeRotationQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Extract the data."""
        return RelativeRotation(
            query.data,
            query.benchmark,
            study=query.study,
            long_period=query.long_period,
            short_period=query.short_period,
            window=query.window,
            trading_periods=query.trading_periods,
        ).__dict__

    @staticmethod
    def transform_data(
        query: RelativeRotationQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> RelativeRotationData:
        """Transform the data."""
        return RelativeRotationData.model_validate(data)
