"""Options Router."""

from typing import Literal, Optional, Union

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
            description='Use the "date" parameter to get the end-of-day-data for a specific date, where supported.',
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
    """Get the complete options chain for a ticker."""
    return await OBBject.from_query(Query(**locals()))


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Filter and process options chains data for volatility.",
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
    data: Union[list[Data], Data],
    target: str = "implied_volatility",
    underlying_price: Optional[float] = None,
    option_type: Optional[Literal["otm", "itm", "calls", "puts"]] = "otm",
    dte_min: Optional[int] = None,
    dte_max: Optional[int] = None,
    moneyness: Optional[float] = None,
    strike_min: Optional[float] = None,
    strike_max: Optional[float] = None,
    oi: bool = False,
    volume: bool = False,
    theme: Literal["dark", "light"] = "dark",
    chart_params: Optional[dict] = None,
) -> OBBject:
    """Filter and process the options chains data for volatility.

    Data posted can be an instance of OptionsChainsData,
    a pandas DataFrame, or a list of dictionaries.
    Data should contain the fields:

    - `expiration`: The expiration date of the option.
    - `strike`: The strike price of the option.
    - `option_type`: The type of the option (call or put).
    - `implied_volatility`: The implied volatility of the option. Or 'target' field.
    - `open_interest`: The open interest of the option.
    - `volume`: The trading volume of the option.
    - `dte` : Optional, days to expiration (DTE) of the option.
    - `underlying_price`: Optional, the price of the underlying asset.

    Results from the `/derivatives/options/chains` endpoint are the preferred input.

    If `underlying_price` is not supplied in the data as a field, it must be provided as a parameter.

    Parameters
    -----------
    data: Union[list[Data], Data]
    target: str
        The field to use as the z-axis. Default is "implied_volatility".
    underlying_price: Optional[float]
        The price of the underlying asset.
    option_type: Optional[str] = "otm"
        The type of df to display. Default is "otm".
        Choices are: ["otm", "itm", "puts", "calls"]
    dte_min: Optional[int] = None
        Minimum days to expiration (DTE) to filter options.
    dte_max: Optional[int] = None
        Maximum days to expiration (DTE) to filter options.
    moneyness: Optional[float] = None
        Specify a % moneyness to target for display,
        entered as a value between 0 and 100.
    strike_min: Optional[float] = None
        Minimum strike price to filter options.
    strike_max: Optional[float] = None
        Maximum strike price to filter options.
    oi: bool = False
        Filter for only options that have open interest. Default is False.
    volume: bool = False
        Filter for only options that have trading volume. Default is False.
    chart: bool = False
        Whether to return a chart or not. Default is False.
        Only valid if `openbb-charting` is installed.
    theme: Literal["dark", "light"] = "dark"
        The theme to use for the chart. Default is "dark".
        Only valid if `openbb-charting` is installed.
    chart_params: Optional[dict] = None
        Additional parameters to pass to the charting library.
        Only valid if `openbb-charting` is installed.
        Valid keys are:
        - `title`: The title of the chart.
        - `xtitle`: Title for the x-axis.
        - `ytitle`: Title for the y-axis.
        - `ztitle`: Title for the z-axis.
        - `colorscale`: The colorscale to use for the chart.
        - `layout_kwargs`: Additional dictionary to be passed to `fig.update_layout` before output.

    Returns
    -------
    OBBject[list]
        An OBBject containing the processed options data.
        Results are a list of dictionaries.
    """
    # pylint: disable=import-outside-toplevel
    from datetime import datetime  # noqa
    from pandas import concat, DataFrame

    df = DataFrame()

    if not data:
        raise OpenBBError("No data to process!")

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
            df = DataFrame(
                [d.model_dump(exclude_none=True, exclude_unset=True) for d in data]  # type: ignore
            )

    options = DataFrame(df.copy())

    last_price = underlying_price or options.underlying_price.iloc[0]  # type: ignore

    if last_price is None:
        raise OpenBBError(
            ValueError(
                "Last price must be provided for options filtering, and was not found in the data."
            )
        )

    if target not in options.columns:  # type: ignore
        raise OpenBBError(f"Error: No {target} field found.")
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
            "Last price must be provided for OTM/ITM options filtering,"
            " and was not found in the data."
        )

    if option_type is not None and option_type == "otm":
        otm_calls = calls.query("strike > @last_price").set_index(  # type: ignore
            ["expiration", "strike", "option_type"]
        )
        otm_puts = puts.query("strike < @last_price").set_index(  # type: ignore
            ["expiration", "strike", "option_type"]
        )
        df = concat([otm_calls, otm_puts]).sort_index().reset_index()
    elif option_type is not None and option_type == "itm":
        itm_calls = calls.query("strike < @last_price").set_index(  # type: ignore
            ["expiration", "strike", "option_type"]
        )
        itm_puts = puts.query("strike > @last_price").set_index(  # type: ignore
            ["expiration", "strike", "option_type"]
        )
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
            description="Use the 'symbol' parameter to get the most recent activity for a specific symbol.",
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
    """Get the complete options chain for a ticker."""
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
    """Get a snapshot of the options market universe."""
    return await OBBject.from_query(Query(**locals()))
