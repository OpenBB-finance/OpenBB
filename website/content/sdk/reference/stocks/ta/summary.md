---
title: summary
description: The page contains two essential open-source tools, FinBrain's model for
  technical summary reports and a viewer for those reports. Learn how to populate
  a technical summary and how to view a summary chart.
keywords:
- Open-source tools
- FinBrain model
- Technical summary reports
- Summary chart
- OpenBB's API
- Stocks
- Ticker symbol
- Technical Analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ta.summary - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get technical summary report provided by FinBrain's API

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/technical_analysis/finbrain_model.py#L15)]

```python
openbb.stocks.ta.summary(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get the technical summary | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| str | technical summary report |
---

</TabItem>
<TabItem value="view" label="Chart">

Print technical summary report provided by FinBrain's API

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/technical_analysis/finbrain_view.py#L14)]

```python
openbb.stocks.ta.summary_chart(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get the technical summary | None | False |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
