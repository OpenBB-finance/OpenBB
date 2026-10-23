"""Relative-rotation router module."""

from openbb_core.app.model.example import APIEx, PythonEx
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router

from openbb_technical.relative_rotation import (
    RelativeRotationData,
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
    params: RelativeRotationQueryParams,
) -> OBBject[RelativeRotationData]:
    """Compute the Relative Rotation Graph (RRG) for a basket against a benchmark."""
    return OBBject(
        results=RelativeRotationFetcher.transform_data(
            params, RelativeRotationFetcher.extract_data(params, {})
        )
    )


__all__ = ["RelativeRotationQueryParams", "relative_rotation", "router"]
