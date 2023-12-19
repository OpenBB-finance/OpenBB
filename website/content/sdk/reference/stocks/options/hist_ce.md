---
title: hist_ce
description: 'This page describes two main functionalities of the OpenBBFinance documentation:
  ''hist_ce'' function for getting historical prices for a specific stock option and
  ''hist_ce_chart'' function for displaying the same historical stock data in charts.
  Both functions come with detailed explanations of their parameters and expected
  returns.'
keywords:
- OpenBBFinance documentation
- stock options
- historical prices
- chart visualization
- hist_ce function
- hist_ce_chart function
- stock data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.hist_ce - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Historic prices for a specific option [chartexchange]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/chartexchange_model.py#L19)]

```python
openbb.stocks.options.hist_ce(symbol: str = "GME", date: str = "2021-02-05", call: bool = True, price: Union[str, int, float] = "90")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get historical data from | GME | True |
| date | str | Date as a string YYYYMMDD | 2021-02-05 | True |
| call | bool | Whether to show a call or a put | True | True |
| price | Union[str, Union[int, float]] | Strike price for a specific option | 90 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Historic information for an option |
---

</TabItem>
<TabItem value="view" label="Chart">

Return raw stock data[chartexchange]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/chartexchange_view.py#L59)]

```python
openbb.stocks.options.hist_ce_chart(symbol: str = "GME", expiry: str = "2021-02-05", call: bool = True, price: float = 90, limit: int = 10, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol for the given option | GME | True |
| expiry | str | The expiry of expiration, format "YYYY-MM-DD", i.e. 2010-12-31. | 2021-02-05 | True |
| call | bool | Whether the underlying asset should be a call or a put | True | True |
| price | float | The strike of the expiration | 90 | True |
| limit | int | Number of rows to show | 10 | True |
| export | str | Export data as CSV, JSON, XLSX |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
