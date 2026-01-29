"""期权路由器。"""

from typing import Literal

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.standard_models.options_chains import OptionsChainsData

router = Router(prefix="/options")

# pylint: disable=unused-argument


@router.command(
    model="OptionsChains",
    examples=[
        APIEx(parameters={"symbol": "AAPL", "provider": "intrinio"}),
        APIEx(
            description='使用 "date" 参数获取特定日期的日终数据（如支持）。',
            parameters={"symbol": "AAPL", "date": "2023-01-25", "provider": "intrinio"},
        ),
    ],
)
async def chains(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取股票代码的完整期权链。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="筛选并处理期权链数据的波动率。",
            code=[
                "data = obb.derivatives.options.chains('AAPL', provider='cboe')",
                "surface = "
                + "obb.derivatives.options.surface(data=data.results, moneyness=20, dte_min=10, dte_max=60, chart=True)",
                "surface.show()",
            ],
        ),
    ],
)
async def surface(  # pylint: disable=R0913, R0917
    data: list[Data] | Data,
    target: str = "implied_volatility",
    underlying_price: float | None = None,
    option_type: Literal["otm", "itm", "calls", "puts"] | None = "otm",
    dte_min: int | None = None,
    dte_max: int | None = None,
    moneyness: float | None = None,
    strike_min: float | None = None,
    strike_max: float | None = None,
    oi: bool = False,
    volume: bool = False,
    theme: Literal["dark", "light"] = "dark",
    chart_params: dict | None = None,
) -> OBBject:
    """过滤和处理期权链数据的波动性。

    发布的数据可以是 OptionsChainsData 的实例，
    pandas DataFrame 或字典列表。
    数据应包含以下字段：

    - `expiration`: 期权的到期日期。
    - `strike`: 期权的行权价。
    - `option_type`: 期权的类型（看涨或看跌）。
    - `implied_volatility`: 期权的隐含波动率。或是 'target' 字段。
    - `open_interest`: 期权的未平仓合约。
    - `volume`: 期权的交易量。
    - `dte` : 可选，期权的到期天数 (DTE)。
    - `underlying_price`: 可选，标的资产的价格。

    首选输入是来自 `/derivatives/options/chains` 端点的结果。

    如果数据中未提供 `underlying_price` 字段，则必须将其作为参数提供。

    Parameters
    -----------
    data: Union[list[Data], Data]
    target: str
        用作 z 轴的字段。默认为 "implied_volatility"。
    underlying_price: Optional[float]
        标的资产的价格。
    option_type: Optional[str] = "otm"
        要显示的 df 类型。默认为 "otm"。
        选项包括：["otm", "itm", "puts", "calls"]
    dte_min: Optional[int] = None
        筛选期权的最小到期天数 (DTE)。
    dte_max: Optional[int] = None
        筛选期权的最大到期天数 (DTE)。
    moneyness: Optional[float] = None
        指定要显示的价内/外程度百分比，
        输入 0 到 100 之间的值。
    strike_min: Optional[float] = None
        筛选期权的最小行权价。
    strike_max: Optional[float] = None
        筛选期权的最大行权价。
    oi: bool = False
        仅筛选有未平仓合约的期权。默认为 False。
    volume: bool = False
        仅筛选有交易量的期权。默认为 False。
    chart: bool = False
        是否返回图表。默认为 False。
        仅当安装了 `openbb-charting` 时有效。
    theme: Literal["dark", "light"] = "dark"
        图表使用的主题。默认为 "dark"。
        仅当安装了 `openbb-charting` 时有效。
    chart_params: Optional[dict] = None
        传递给图表库的其他参数。
        仅当安装了 `openbb-charting` 时有效。
        有效键为：
        - `title`: 图表的标题。
        - `xtitle`: x 轴的标题。
        - `ytitle`: y 轴的标题。
        - `ztitle`: z 轴的标题。
        - `colorscale`: 用于图表的色标。
        - `layout_kwargs`: 在输出前传递给 `fig.update_layout` 的附加字典。

    Returns
    -------
    OBBject[list]
        包含处理过期权数据的 OBBject。
        结果是字典列表。
    """
    # pylint: disable=import-outside-toplevel
    from datetime import datetime  # noqa
    from pandas import concat, DataFrame

    df = DataFrame()

    if not data:
        raise OpenBBError("没有要处理的数据！")

    if isinstance(data, OptionsChainsData):
        df = data.dataframe
    elif isinstance(data, DataFrame):
        df = data
    elif isinstance(data, dict) and all(isinstance(v, list) for v in data.values()):
        df = DataFrame(data)
    elif isinstance(data, list):
        if all(isinstance(d, dict) for d in data):
            df = DataFrame(data)
        elif all(isinstance(d, Data) for d in data):
            df = DataFrame([d.model_dump(exclude_none=True, exclude_unset=True) for d in data])  # type: ignore

    options = DataFrame(df.copy())

    last_price = underlying_price or options.underlying_price.iloc[0]  # type: ignore

    if last_price is None:
        raise OpenBBError(
            ValueError(
                "必须为期权筛选提供最新价格，但在数据中未找到。"
            )
        )

    if target not in options.columns:  # type: ignore
        raise OpenBBError(f"错误: 未找到 {target} 字段。")
    if "dte" not in options.columns:  # type: ignore
        options.dte = (options.expiration - datetime.today().date()).days  # type: ignore

    calls = options.query(f"`option_type` == 'call' and `dte` >= 0 and `{target}` > 0")  # type: ignore
    puts = options.query(f"`option_type` == 'put' and `dte` >= 0 and `{target}` > 0")  # type: ignore

    if oi:
        calls = calls[calls["open_interest"] > 0]
        puts = puts[puts["open_interest"] > 0]

    if volume:
        calls = calls[calls["volume"] > 0]
        puts = puts[puts["volume"] > 0]

    if dte_min is not None:
        calls = calls.query("dte >= @dte_min")  # type: ignore
        puts = puts.query("dte >= @dte_min")  # type: ignore

    if dte_max is not None:
        calls = calls.query("dte <= @dte_max")  # type: ignore
        puts = puts.query("dte <= @dte_max")  # type: ignore

    if moneyness is not None and moneyness > 0:
        moneyness = float(moneyness)
        high = (  # noqa:F841 pylint: disable=unused-variable  # type: ignore
            1 + (moneyness / 100)
        ) * last_price
        low = (  # noqa:F841 pylint: disable=unused-variable  # type: ignore
            1 - (moneyness / 100)
        ) * last_price
        calls = calls.query("@low <= `strike` <= @high")  # type: ignore
        puts = puts.query("@low <= `strike` <= @high")  # type: ignore

    if strike_min is not None:
        calls = calls.query("strike >= @strike_min")  # type: ignore
        puts = puts.query("strike >= @strike_min")  # type: ignore

    if strike_max is not None:
        calls = calls.query("strike <= @strike_max")  # type: ignore
        puts = puts.query("strike <= @strike_max")  # type: ignore

    if option_type in ["otm", "itm"] and last_price is None:
        raise RuntimeError(
            "必须为 OTM/ITM 期权筛选提供最新价格，但在数据中未找到。"
        )

    if option_type is not None and option_type == "otm":
        otm_calls = calls.query("strike > @last_price").set_index(["expiration", "strike", "option_type"])  # type: ignore
        otm_puts = puts.query("strike < @last_price").set_index(["expiration", "strike", "option_type"])  # type: ignore
        df = concat([otm_calls, otm_puts]).sort_index().reset_index()
    elif option_type is not None and option_type == "itm":
        itm_calls = calls.query("strike < @last_price").set_index(["expiration", "strike", "option_type"])  # type: ignore
        itm_puts = puts.query("strike > @last_price").set_index(["expiration", "strike", "option_type"])  # type: ignore
        df = concat([itm_calls, itm_puts]).sort_index().reset_index()
    elif option_type is not None and option_type == "calls":
        df = calls
    elif option_type is not None and option_type == "puts":
        df = puts

    df = DataFrame(
        df[  # type: ignore
            [
                "expiration",
                "strike",
                "option_type",
                "dte",
                target,
                "open_interest",
                "volume",
            ]
        ]
    )

    return OBBject(results=df.to_dict(orient="records"))


@router.command(
    model="OptionsUnusual",
    examples=[
        APIEx(parameters={"symbol": "TSLA", "provider": "intrinio"}),
        APIEx(
            description="使用 'symbol' 参数获取特定代码的最新活动。",
            parameters={"symbol": "TSLA", "provider": "intrinio"},
        ),
    ],
)
async def unusual(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取股票代码的完整期权链。"""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    model="OptionsSnapshots",
    examples=[
        APIEx(
            parameters={"provider": "intrinio"},
        ),
    ],
)
async def snapshots(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject:
    """获取期权市场全景的快照。"""
    return await OBBject.from_query(Query(**locals()))
