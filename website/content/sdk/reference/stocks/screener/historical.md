---
title: historical
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# historical

<Tabs>
<TabItem value="model" label="Model" default>

View historical price of stocks that meet preset

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/screener/yahoofinance_model.py#L53)]

```python
openbb.stocks.screener.historical(preset_loaded: str = "top_gainers", limit: int = 10, start_date: str = "2022-05-29", type_candle: str = "a", normalize: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset_loaded | str | Preset loaded to filter for tickers | top_gainers | True |
| limit | int | Number of stocks to display | 10 | True |
| start_date | str | Start date to display historical data, in YYYY-MM-DD format | 2022-05-29 | True |
| type_candle | str | Type of candle to display | a | True |
| normalize | bool | Boolean to normalize all stock prices using MinMax | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of the screener |
---



</TabItem>
<TabItem value="view" label="Chart">

View historical price of stocks that meet preset

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/screener/yahoofinance_view.py#L28)]

```python
openbb.stocks.screener.historical_chart(preset_loaded: str = "top_gainers", limit: int = 10, start_date: str = "2022-05-29", type_candle: str = "a", normalize: bool = True, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset_loaded | str | Preset loaded to filter for tickers | top_gainers | True |
| limit | int | Number of stocks to display | 10 | True |
| start_date | str | Start date to display historical data, in YYYY-MM-DD format | 2022-05-29 | True |
| type_candle | str | Type of candle to display | a | True |
| normalize | bool | Boolean to normalize all stock prices using MinMax | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| list[str] | List of stocks |
---



</TabItem>
</Tabs>