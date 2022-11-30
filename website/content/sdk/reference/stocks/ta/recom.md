---
title: recom
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# recom

<Tabs>
<TabItem value="model" label="Model" default>

Get tradingview recommendation based on technical indicators

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/technical_analysis/tradingview_model.py#L56)]

```python
openbb.stocks.ta.recom(symbol: str, screener: str = "america", exchange: str = "", interval: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get the recommendation from tradingview based on technical indicators | None | False |
| screener | str | Screener based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html | america | True |
| exchange | str | Exchange based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html |  | True |
| interval | str | Interval time to check technical indicators and correspondent recommendation |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of tradingview recommendations based on technical indicators |
---



</TabItem>
<TabItem value="view" label="Chart">

Print tradingview recommendation based on technical indicators

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/technical_analysis/tradingview_view.py#L17)]

```python
openbb.stocks.ta.recom_chart(symbol: str, screener: str = "america", exchange: str = "", interval: str = "", export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get tradingview recommendation based on technical indicators | None | False |
| screener | str | Screener based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html | america | True |
| exchange | str | Exchange based on tradingview docs https://python-tradingview-ta.readthedocs.io/en/latest/usage.html |  | True |
| interval | str | Interval time to check technical indicators and correspondent recommendation |  | True |
| export | str | Format of export file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>