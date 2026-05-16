"""Relative-rotation router module."""

from typing import Any, Literal

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.provider.abstract.data import Data

from openbb_technical.relative_rotation import (
    RelativeRotationFetcher,
    RelativeRotationQueryParams,
)

router = Router(prefix="", description="Relative rotation indicator.")


@router.command(
    methods=["POST"],
    examples=[
        PythonEx(
            description="Relative Strength Ratio and Momentum for a basket of symbols against a benchmark.",
            code=[
                "data = obb.equity.price.historical(symbol='AAPL,MSFT,GOOGL,META,AMZN,TSLA,SPY', start_date='2022-01-01', provider='yfinance').results",
                "rr = obb.technical.relative_rotation(data=data, benchmark='SPY')",
            ],
        ),
        APIEx(parameters={"data": APIEx.mock_data("timeseries"), "benchmark": "SPY"}),
    ],
)
async def relative_rotation(
    data: list[Data],
    benchmark: str,
    study: Literal["price", "volume", "volatility"] = "price",
    long_period: int | None = 252,
    short_period: int | None = 21,
    window: int | None = 21,
    trading_periods: int | None = 252,
    chart_params: dict[str, Any] | None = None,
) -> OBBject:
    """Compute the Relative Rotation Graph (RRG) for a basket against a benchmark.

    The Relative Rotation Graph plots two normalised series for each symbol —
    the JdK RS-Ratio (relative-strength level vs. the benchmark, mean-100
    standardised over ``long_period``) and the JdK RS-Momentum (the rate of
    change of RS-Ratio, mean-100 standardised over ``short_period``). The two
    series locate each symbol in one of four quadrants of the RRG plane:
    leading (>100/>100), weakening (>100/<100), lagging (<100/<100), and
    improving (<100/>100). Symbols rotate clockwise through the quadrants
    over time, so the trail of points across the most-recent ``window`` bars
    reveals momentum-driven leadership changes within a basket.

    Parameters
    ----------
    data : list[Data]
        Long-format multi-symbol price (or volume / volatility) series. Must
        contain the benchmark symbol and at least one constituent.
    benchmark : str
        Symbol used as the relative-strength denominator.
    study : {"price", "volume", "volatility"}, optional
        Series to compute relative strength on, by default ``"price"``.
    long_period : int, optional
        Lookback for RS-Ratio standardisation, by default 252 (≈1 year of
        daily bars).
    short_period : int, optional
        Lookback for RS-Momentum standardisation, by default 21.
    window : int, optional
        Number of trailing bars to retain in the rotation trail, by default 21.
    trading_periods : int, optional
        Bars per year used for annualisation when ``study='volatility'``,
        by default 252.
    chart_params : dict[str, Any], optional
        Charting-extension overrides forwarded verbatim; ignored when no
        chart is requested.

    Returns
    -------
    OBBject[RelativeRotationData]
        RS-Ratio and RS-Momentum time series per symbol plus benchmark
        metadata, ready for direct consumption by the relative-rotation
        chart helper.
    """
    params = RelativeRotationQueryParams(
        data=data,
        benchmark=benchmark,
        study=study,
        long_period=long_period,
        short_period=short_period,
        window=window,
        trading_periods=trading_periods,
        chart_params=chart_params,
    )
    return OBBject(
        results=RelativeRotationFetcher.transform_data(
            params, RelativeRotationFetcher.extract_data(params, {})
        )
    )


__all__ = ["relative_rotation", "router"]
