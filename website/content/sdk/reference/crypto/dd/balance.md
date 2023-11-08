---
title: balance
description: This page provides documentation on the 'balance' functions, enabling
  users to view account holdings for particular assets. It dives into the specifics
  of how to use these functions to retrieve data from Binance and display it efficiently.
keywords:
- balance functions
- account holdings
- asset
- Binance
- cryptocurrency
- dataframe
- parameters
- balance_chart function
- export dataframe
- USDT
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.dd.balance - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get account holdings for asset. [Source: Binance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/binance_model.py#L179)]

```python
openbb.crypto.dd.balance(from_symbol: str, to_symbol: str = "USDT")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| from_symbol | str | Cryptocurrency | None | False |
| to_symbol | str | Cryptocurrency | USDT | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with account holdings for an asset |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing account holdings for asset. [Source: Binance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/binance_view.py#L64)]

```python
openbb.crypto.dd.balance_chart(from_symbol: str, to_symbol: str = "USDT", export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| from_symbol | str | Cryptocurrency | None | False |
| to_symbol | str | Cryptocurrency | USDT | True |
| export | str | Export dataframe data to csv,json,xlsx |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
