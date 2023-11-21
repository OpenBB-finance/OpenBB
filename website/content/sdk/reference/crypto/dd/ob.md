---
title: ob
description: This documentation page provides detailed information about operation
  of generating and viewing order book for a coin in a given exchange using OpenBB
  library. Learn about the parameters required and the response for each function
  call.
keywords:
- orderbook
- openbb.crypto.dd
- cryptocurrency
- coin exchange
- ob
- ob_chart
- coin symbol
- exchange id
- crypto trading
- matplotlib.axes._axes.Axes
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.ob - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns orderbook for a coin in a given exchange

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/ccxt_model.py#L46)]

```python
openbb.crypto.dd.ob(exchange: str, symbol: str, to_symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| exchange | str | exchange id | None | False |
| symbol | str | coin symbol | None | False |
| to_symbol | str | currency to compare coin against | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Dict[str, Any] | With bids and asks |
---

</TabItem>
<TabItem value="view" label="Chart">

Plots order book for a coin in a given exchange

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/ccxt_view.py#L19)]

```python
openbb.crypto.dd.ob_chart(exchange: str, symbol: str, to_symbol: str, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| exchange | str | exchange id | None | False |
| symbol | str | coin symbol | None | False |
| vs | str | currency to compare coin against | None | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
