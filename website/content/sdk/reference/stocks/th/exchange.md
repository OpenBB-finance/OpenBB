---
title: exchange
description: This documentation page provides details on the 'exchange' function of
  the OpenBB platform. This includes the model function for acquiring current exchange
  open hours, and the view function for displaying these hours. The page provides
  information on source codes, parameters and return values.
keywords:
- exchange
- trading hours
- model
- view
- chart
- parameters
- returns
- dataframe
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.th.exchange - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get current exchange open hours.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/tradinghours/bursa_model.py#L20)]

```python
openbb.stocks.th.exchange(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Exchange symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Exchange info |
---

</TabItem>
<TabItem value="view" label="Chart">

Display current exchange trading hours.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/tradinghours/bursa_view.py#L15)]

```python
openbb.stocks.th.exchange_chart(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Exchange symbol | None | False |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
