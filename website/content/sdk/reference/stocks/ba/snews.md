---
title: snews
description: snews is an impactful tool from OpenBB's finance package employing VADER
  sentiment model to analyze stock headline sentiments over time, leveraged from Finnhub
  data. It also provides features to visualize these sentiments against the stock
  price using Python's matplotlib library.
keywords:
- snews
- VADER model
- Finnhub
- stock sentiment analysis
- OpenBB finance
- trading strategies
- data visualization
- matplotlib
- sentiment over time
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.snews - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get headlines sentiment using VADER model over time. [Source: Finnhub]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/behavioural_analysis/finnhub_model.py#L100)]

```python wordwrap
openbb.stocks.ba.snews(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker of company | None | False |
| Returns | None |  | None | True |
| ---------- | None |  | None | True |
| pd.DataFrame | None | The news article information | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
<TabItem value="view" label="Chart">

Display stock price and headlines sentiment using VADER model over time. [Source: Finnhub]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/behavioural_analysis/finnhub_view.py#L21)]

```python wordwrap
openbb.stocks.ba.snews_chart(symbol: str, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker of company | None | False |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>