---
title: candles
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# candles

<Tabs>
<TabItem value="model" label="Model" default>

## forex_oanda_model.get_candles_dataframe

```python title='openbb_terminal/forex/oanda/oanda_model.py'
def get_candles_dataframe(instrument: Optional[str], granularity: str, candlecount: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L581)

Description: Request data for candle chart.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| instrument | str | Loaded currency pair code | None | False |
| granularity | str | Data granularity, by default "D" | None | True |
| candlecount | int | Limit for the number of data points, by default 180 | 180 | True |

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, bool] | Candle chart data or False |

## Examples



</TabItem>
<TabItem value="view" label="View">

## forex_oanda_view.show_candles

```python title='openbb_terminal/decorators.py'
def show_candles() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L304)

Description: Show candle chart.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| instrument | str | The loaded currency pair | None | False |
| granularity | str | The timeframe to get for the candle chart. Seconds: S5, S10, S15, S30
Minutes: M1, M2, M4, M5, M10, M15, M30 Hours: H1, H2, H3, H4, H6, H8, H12
Day (default): D, Week: W Month: M, | None | True |
| candlecount | int | Limit for the number of data points | None | True |
| additional_charts | Dict[str, bool] | A dictionary of flags to include additional charts | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>