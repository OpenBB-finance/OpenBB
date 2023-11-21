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

Scrape barchart for options info

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/barchart_model.py#L16)]

```python wordwrap
openbb.stocks.options.info(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of options information |
---



</TabItem>
<TabItem value="view" label="Chart">

Scrapes Barchart.com for the options information

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/barchart_view.py#L16)]

```python wordwrap
openbb.stocks.options.info_chart(symbol: str, export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get options info for | None | False |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format of export file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>