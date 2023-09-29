---
title: eb
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# eb

<Tabs>
<TabItem value="model" label="Model" default>

Returns the total amount of coins held on exchange addresses in units and percentage.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/glassnode_model.py#L453)]

```python
openbb.crypto.dd.eb(symbol: str, exchange: str = "aggregated", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Asset to search active addresses (e.g., BTC) | None | False |
| exchange | str | Exchange to check net position change (possible values are: aggregated, binance, bittrex,<br/>coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex, hitbtc, kraken,<br/>okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno), by default "aggregated" | aggregated | True |
| start_date | Optional[str] | Initial date (format YYYY-MM-DD) by default 2 years ago | None | True |
| end_date | Optional[str] | Final date (format YYYY-MM-DD) by default 1 year ago | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | total amount of coins in units/percentage and symbol price over time |
---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.crypto.dd.eb(symbol="BTC")
```

---



</TabItem>
<TabItem value="view" label="Chart">

Plots total amount of coins held on exchange addresses in units and percentage.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/glassnode_view.py#L238)]

```python
openbb.crypto.dd.eb_chart(symbol: str, exchange: str = "aggregated", start_date: Optional[str] = None, end_date: Optional[str] = None, percentage: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Asset to search active addresses (e.g., BTC) | None | False |
| exchange | str | Exchange to check net position change (possible values are: aggregated, binance, bittrex,<br/>coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex, hitbtc, kraken,<br/>okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno), by default "aggregated" | aggregated | True |
| start_date | Optional[str] | Initial date (format YYYY-MM-DD) by default 2 years ago | None | True |
| end_date | Optional[str] | Final date (format YYYY-MM-DD) by default 1 year ago | None | True |
| percentage | bool | Show percentage instead of stacked value. | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.crypto.dd.eb_chart(symbol="BTC")
```

---



</TabItem>
</Tabs>