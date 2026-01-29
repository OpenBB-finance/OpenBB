"""相对旋转模型。"""

# pylint: disable=too-many-arguments, too-many-instance-attributes, protected-access
# pylint: disable=too-many-locals, too-few-public-methods, unused-argument

from typing import TYPE_CHECKING, Any, Literal, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator

if TYPE_CHECKING:
    from pandas import DataFrame, Series


def absolute_maximum_scale(data: "Series") -> "Series":
    """绝对最大值缩放归一化方法。"""
    return data / data.abs().max()


def min_max_scaling(data: "Series") -> "Series":
    """最小/最大缩放归一化方法。"""
    return (data - data.min()) / (data.max() - data.min())


def z_score_standardization(data: "Series") -> "Series":
    """Z-Score 标准化方法。"""
    return (data - data.mean()) / data.std()


def normalize(data: "DataFrame", method: Literal["z", "m", "a"] = "z") -> "DataFrame":
    """
    根据方法归一化 Pandas DataFrame。

    Parameters
    ----------
    data: "DataFrame"
        具有任意数量列的 Pandas DataFrame，需要进行归一化。
    method: Literal["z", "m", "a"]
        归一化方法。
            z: Z-Score 标准化
            m: 最小/最大缩放
            a: 绝对最大值缩放

    Returns
    -------
    DataFrame
        归一化后的 DataFrame。
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
    data: "DataFrame",
    window: int = 21,
    trading_periods: int = 252,
) -> "DataFrame":
    """
    衡量回报从平均回报分散的程度。

    它是最常见（且有偏差）的波动率估计量。

    Parameters
    ----------
    data : pd.DataFrame
        OHLC 价格数据框。
    window : int [default: 21]
        用于计算的窗口长度。
    trading_periods : Optional[int] [default: 252]
        即每年的交易周期数。

    Returns
    -------
    pd.DataFrame : results
        包含结果的数据框。
    """
    # pylint: disable=import-outside-toplevel
    from numpy import log, sqrt
    from pandas import DataFrame

    data = data.copy()
    results = DataFrame()
    if window < 2:
        window = 21

    for col in data.columns.tolist():
        log_return = (data[col] / data[col].shift(1)).apply(log)

        result = log_return.rolling(window=window, center=False).std() * sqrt(
            trading_periods
        )
        results[col] = result

    return results.dropna()


def calculate_momentum(
    data: "Series", long_period: int = 252, short_period: int = 21
) -> "Series":
    """
    动量计算为对数过去 12 个月回报减去过去一个月回报。

    较高的值表示较大的正动量敞口。

    Momentum = ln(1 + r12) - ln(1 + r1)

    Parameters
    ----------
    data: "Series"
        用于计算动量的时间序列数据。
    long_period: Optional[int]
        计算基础的长周期。默认为一个标准交易年。
    short_period: Optional[int]
        从长周期中减去的短周期。默认为一个交易月。

    Returns
    -------
    Series
        包含计算动量的 Pandas Series。
    """
    # pylint: disable=import-outside-toplevel
    from numpy import log

    df = data.copy()
    epsilon = 1e-10
    momentum_long = log(1 + df.pct_change(long_period) + epsilon)
    momentum_short = log(1 + df.pct_change(short_period) + epsilon)
    data = momentum_long - momentum_short  # type: ignore

    return data


def get_momentum(
    data: "DataFrame", long_period: int = 252, short_period: int = 21
) -> "DataFrame":
    """
    计算相对强度动量指标。

    以相对强度比率作为输入。

    Parameters
    ----------
    data: "DataFrame"
        格式化的索引时间序列数据，每列代表一个股票代码。
    long_period: Optional[int]
        计算基础的长周期。默认为一个标准交易年。
    short_period: Optional[int]
        从长周期中减去的短周期。默认为一个交易月。

    Returns
    -------
    DataFrame
        包含计算出的历史动量因子敞口分数的 Pandas DataFrame。
    """
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame

    df = data.copy()
    rs_momentum = DataFrame()
    for ticker in df.columns.to_list():
        rs_momentum.loc[:, ticker] = calculate_momentum(df.loc[:, ticker], long_period, short_period)  # type: ignore

    return rs_momentum


def calculate_relative_strength_ratio(
    symbols_data: "DataFrame",
    benchmark_data: "DataFrame",
) -> "DataFrame":
    """计算 DataFrame 中每个股票代码（列）相对于基准的相对强度比率。

    股票代码数据和基准数据应具有相同的索引，
    并且每列应代表一个股票代码。

    Parameters
    ----------
    symbols_data: "DataFrame"
        包含要与基准进行比较的股票代码数据的 Pandas DataFrame。
    benchmark_data: "DataFrame"
        包含基准数据的 Pandas DataFrame。

    Returns
    -------
    DataFrame
        包含每个股票代码的计算相对强度比率与基准值连接的 Pandas DataFrame。
    """
    return (
        symbols_data.div(benchmark_data.iloc[:, 0], axis=0)
        .multiply(100)
        .join(benchmark_data.iloc[:, 0])
        .dropna()
    )


def process_data(
    symbols_data: "DataFrame",
    benchmark_data: "DataFrame",
    long_period: int = 252,
    short_period: int = 21,
    normalize_method: Literal["z", "m", "a"] = "z",
) -> tuple["DataFrame", "DataFrame"]:
    """将原始数据处理为归一化指标值。

    Parameters
    ----------
    symbols_data: "DataFrame"
        格式化的索引时间序列数据，每列代表一个股票代码。
    benchmark_data: "DataFrame"
        基准代码的索引时间序列数据。
    long_period: Optional[int]
        计算基础的长周期。默认为一个标准交易年。
    short_period: Optional[int]
        从长周期中减去的短周期。默认为一个交易月。
    normalize_method: Literal["z", "m", "a"]

    Returns
    -------
    Tuple[DataFrame, DataFrame]
        包含归一化比率和动量指标值的 Pandas DataFrame 元组。
    """
    ratio_data = calculate_relative_strength_ratio(symbols_data, benchmark_data)
    momentum_data = get_momentum(ratio_data, long_period, short_period)
    normalized_ratio = normalize(ratio_data, normalize_method)
    normalized_momentum = normalize(momentum_data, normalize_method)

    return normalized_ratio, normalized_momentum


class RelativeRotation:
    """相对旋转类。"""

    def __init__(  # pylint: disable=R0917
        self,
        data: Union[list[Data], "DataFrame"],
        benchmark: str,
        study: Literal["price", "volume", "volatility"] | None = "price",
        long_period: int | None = 252,
        short_period: int | None = 21,
        window: int | None = 21,
        trading_periods: int | None = 252,
    ):
        """Initialize the class."""
        # pylint: disable=import-outside-toplevel
        import contextlib  # noqa
        from openbb_core.app.model.obbject import OBBject  # noqa
        from openbb_core.app.utils import (  # noqa
            basemodel_to_df,
            convert_to_basemodel,
            df_to_basemodel,
        )
        from pandas import DataFrame  # noqa

        benchmark = benchmark.upper()
        df = DataFrame()

        target_col = "volume" if study == "volume" else "close"

        if isinstance(data, OBBject):
            data = data.results  # type: ignore

        if isinstance(data, list) and (
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
        """处理数据。"""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.utils import df_to_basemodel
        from pandas import to_datetime

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
    """获取类型提示的类型名称。"""
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
    """相对旋转查询参数。"""

    data: list[Data] = Field(
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
    long_period: int | None = Field(
        default=252,
        description="The length of the long period for momentum calculation, by default is 252."
        + " Adjust this value, to 365, when supplying assets such as crypto.",
    )
    short_period: int | None = Field(
        default=21,
        description="The length of the short period for momentum calculation, by default is 21."
        + " Adjust this value, to 30, when supplying assets such as crypto.",
    )
    window: int | None = Field(
        default=21,
        description="The length of window for the standard deviation calculation, by default is 21."
        + " Adjust this value, to 30, when supplying assets such as crypto.",
    )
    trading_periods: int | None = Field(
        default=252,
        description="The number of trading periods per year,"
        + " for the standard deviation calculation, by default is 252."
        + " Adjust this value, to 365, when supplying assets such as crypto.",
    )
    chart_params: dict[str, Any] | None = Field(
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
        """将基准代码转换为大写。"""
        return v.upper()

    @field_validator("data", mode="before", check_fields=False)
    @classmethod
    def convert_data(cls, v):
        """验证数据格式。"""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.obbject import OBBject
        from openbb_core.app.utils import convert_to_basemodel, df_to_basemodel
        from pandas import DataFrame

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
        """初始化类。"""
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
    """相对旋转数据模型。"""

    symbols: list[str] = Field(
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
    symbols_data: list[Data] = Field(
        description="The data representing the selected 'study' for each symbol."
    )
    benchmark_data: list[Data] = Field(
        description="The data representing the selected 'study' for the benchmark."
    )
    rs_ratios: list[Data] = Field(
        description="The normalized relative strength ratios data."
    )
    rs_momentum: list[Data] = Field(
        description="The normalized relative strength momentum data."
    )

    def __init__(self, **data):
        """初始化类。"""
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
    """相对旋转获取器。"""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> RelativeRotationQueryParams:
        """转换查询参数。"""
        return RelativeRotationQueryParams.model_validate(**params)

    @staticmethod
    def extract_data(
        query: RelativeRotationQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """提取数据。"""
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
        data: dict,
        **kwargs: Any,
    ) -> RelativeRotationData:
        """转换数据。"""
        return RelativeRotationData.model_validate(data)
