---
title: change
description: This page provides detailed documentation on how to track the 30-day
  change in the supply held in exchange wallets using our function 'openbb.crypto.dd.change'.
  It also includes steps on how to visualize these changes by plotting a chart using
  the function 'openbb.crypto.dd.change_chart'. The page contains explanations about
  each function parameter, return types, and default values along with links to the
  source code.
keywords:
- SEO optimization
- Metadata
- Cryptocurrency Supply Change
- Exchange Wallets
- OpenBB Crypto DD Change
- Plot Change Chart
- OpenBB Crypto DD Change Chart
- Documentation
- Source Code Link
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.change - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns 30d change of the supply held in exchange wallets of a certain symbol.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/glassnode_model.py#L555)]

```python
openbb.crypto.dd.change(symbol: str, exchange: str = "binance", start_date: str = "2010-01-01", end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Asset symbol to search supply (e.g., BTC) | None | False |
| exchange | str | Exchange to check net position change (e.g., binance) | binance | True |
| start_date | Optional[str] | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | supply change in exchange wallets of a certain symbol over time |
---

</TabItem>
<TabItem value="view" label="Chart">

Plots 30d change of the supply held in exchange wallets.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/glassnode_view.py#L157)]

```python
openbb.crypto.dd.change_chart(symbol: str, exchange: str = "binance", start_date: str = "2010-01-01", end_date: Optional[str] = None, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Asset to search active addresses (e.g., BTC) | None | False |
| exchange | str | Exchange to check net position change (possible values are: aggregated, binance,<br/>bittrex, coinex, gate.io, gemini, huobi, kucoin, poloniex, bibox, bigone, bitfinex,<br/>hitbtc, kraken, okex, bithumb, zb.com, cobinhood, bitmex, bitstamp, coinbase, coincheck, luno) | binance | True |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
