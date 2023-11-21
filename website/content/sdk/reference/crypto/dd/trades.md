---
title: trades
description: Documentation of 'trades' in OpenBB.finance. It includes various functions
  for obtaining and displaying trades for a coin in a given exchange. It covers both
  the model and view and provides detailed description of each parameter involved.
keywords:
- trades
- exchange
- coin
- currency
- symbol
- OpenBB.finance
- ccxt model
- ccxt view
- trade chart
- crypto
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.trades - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns trades for a coin in a given exchange

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/ccxt_model.py#L70)]

```python
openbb.crypto.dd.trades(exchange_id: str, symbol: str, to_symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| exchange_id | str | exchange id | None | False |
| symbol | str | coin symbol | None | False |
| to_symbol | str | currency to compare coin against | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | trades for a coin in a given exchange |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing trades for a coin in a given exchange

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/ccxt_view.py#L63)]

```python
openbb.crypto.dd.trades_chart(exchange: str, symbol: str, to_symbol: str, limit: int = 10, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| exchange | str | exchange id | None | False |
| symbol | str | coin symbol | None | False |
| to_symbol | str | currency to compare coin against | None | False |
| limit | int | number of trades to display | 10 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
