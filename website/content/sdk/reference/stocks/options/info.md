---
title: info
description: This documentation page provides information about the info and chart
  models for options in OpenBB Terminal, explaining how to get ticker info and scrape
  Barchart.com for options info.
keywords:
- OpenBB Terminal documentation
- Stock options
- Ticker info
- Barchart.com scraping
- Python utilities
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.info - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get info for a given ticker

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_model.py#L329)]

```python
openbb.stocks.options.info(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | The ticker symbol to get the price for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| float | The info for a given ticker |
---

</TabItem>
<TabItem value="view" label="Chart">

Scrapes Barchart.com for the options information

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/barchart_view.py#L15)]

```python
openbb.stocks.options.info_chart(symbol: str, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get options info for | None | False |
| export | str | Format of export file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
