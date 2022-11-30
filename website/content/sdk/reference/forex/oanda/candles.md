---
title: candles
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# candles

<Tabs>
<TabItem value="model" label="Model" default>

Request data for candle chart.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_model.py#L581)]

```python
openbb.forex.oanda.candles(instrument: Optional[str] = None, granularity: str = "D", candlecount: int = 180)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| instrument | str | Loaded currency pair code | None | True |
| granularity | str | Data granularity, by default "D" | D | True |
| candlecount | int | Limit for the number of data points, by default 180 | 180 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame, bool] | Candle chart data or False |
---



</TabItem>
<TabItem value="view" label="Chart">

Show candle chart.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forex/oanda/oanda_view.py#L294)]

```python
openbb.forex.oanda.candles_chart(instrument: str = "", granularity: str = "D", candlecount: int = 180, additional_charts: Optional[Dict[str, bool]] = None, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| instrument | str | The loaded currency pair |  | True |
| granularity | str | The timeframe to get for the candle chart. Seconds: S5, S10, S15, S30<br/>Minutes: M1, M2, M4, M5, M10, M15, M30 Hours: H1, H2, H3, H4, H6, H8, H12<br/>Day (default): D, Week: W Month: M, | D | True |
| candlecount | int | Limit for the number of data points | 180 | True |
| additional_charts | Dict[str, bool] | A dictionary of flags to include additional charts | None | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>