---
title: mktcap
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# mktcap

<Tabs>
<TabItem value="model" label="Model" default>

Get market cap over time for ticker. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L287)]

```python
openbb.stocks.fa.mktcap(symbol: str, start_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get market cap over time | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 3 years back | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of estimated market cap over time |
---



</TabItem>
<TabItem value="view" label="Chart">

Display market cap over time. [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_view.py#L338)]

```python
openbb.stocks.fa.mktcap_chart(symbol: str, start_date: Optional[str] = None, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 3 years back | None | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>