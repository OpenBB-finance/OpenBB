---
title: income
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# income

<Tabs>
<TabItem value="model" label="Model" default>

Get income data. [Source: Marketwatch].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/marketwatch_model.py#L74)]

```python
openbb.stocks.ca.income(similar: List[str], timeframe: str = "2021", quarter: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of tickers to compare.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| timeframe | str | Column header to compare | 2021 | True |
| quarter | bool | Whether to use quarterly statements, by default False | False | True |
| export | str | Format to export data | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of income statements |
---



</TabItem>
<TabItem value="view" label="Chart">

Display income data. [Source: Marketwatch].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/marketwatch_view.py#L23)]

```python
openbb.stocks.ca.income_chart(symbols: List[str], timeframe: str = "2021", quarter: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of tickers to compare. Enter tickers you want to see as shown below:<br/>["TSLA", "AAPL", "NFLX", "BBY"]<br/>You can also get a list of comparable peers with<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| timeframe | str | What year to look at | 2021 | True |
| quarter | bool | Whether to use quarterly statements, by default False | False | True |
| export | str | Format to export data |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>