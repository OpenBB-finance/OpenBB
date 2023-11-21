---
title: view
description: Technical analysis with OpenBB - Learn how to use finviz model and view
  chart using stock ticker. Detailed examples, parameters, and source code included.
keywords:
- technical analysis
- finviz model
- view chart
- stock ticker
- matplotlib
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ta.view - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get finviz image for given ticker

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/technical_analysis/finviz_model.py#L16)]

```python
openbb.stocks.ta.view(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| bytes | Image in byte format |
---

</TabItem>
<TabItem value="view" label="Chart">

View finviz image for ticker

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/technical_analysis/finviz_view.py#L22)]

```python
openbb.stocks.ta.view_chart(symbol: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
