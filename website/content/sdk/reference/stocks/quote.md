---
title: quote
description: Documentation for 'Ticker quote', a function of OpenBB's Stock Model.
  It retrieves information about a specific ticker from YahooFinance. This tool doesn't
  return any values, it solely utilizes inputted symbols.
keywords:
- Ticker quote
- YahooFinance
- Stock model
- symbol
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.quote - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Gets ticker quote from FMP

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_model.py#L322)]

```python wordwrap
openbb.stocks.quote(symbols: List[str])
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | A list of Stock ticker symbols | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of ticker quote |
---

## Examples


A single ticker must be entered as a list.

```python
df = openbb.stocks.quote(["AAPL"])
```


Multiple tickers can be retrieved.

```python
df = openbb.stocks.quote(["AAPL","MSFT","GOOG","NFLX","META","AMZN","NVDA"])
```

---



</TabItem>
<TabItem value="view" label="Chart">

Financial Modeling Prep ticker(s) quote.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_view.py#L15)]

```python wordwrap
openbb.stocks.quote_chart(symbols: List[str], export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | A list of ticker symbols. | None | False |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |


---

## Returns

This function does not return anything

---

## Examples


This end point displays the results as an interactive table.

```python
from openbb_terminal.sdk import openbb
openbb.stocks.quote_chart(["MSFT"])
```


Multiple tickers are retrieved at once using a comma-separated list.

```python
openbb.stocks.quote_chart(["MSFT","AAPL"])
```

---



</TabItem>
</Tabs>