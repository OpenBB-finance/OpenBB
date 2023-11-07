---
title: baas
description: The 'baas' page details how to get average bid and ask prices, as well
  as the average spread for a given crypto pair over a chosen time period in OpenBBTerminal.
  It explains how to use various parameters for sorting and exporting data.
keywords:
- baas
- crypto pair
- average bid and ask prices
- average spread
- time period
- ERC20 token symbol
- Quoted currency
- sort data
- data ascending
- Export dataframe
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.baas - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get an average bid and ask prices, average spread for given crypto pair for chosen time period.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L725)]

```python
openbb.crypto.onchain.baas(symbol: str = "WETH", to_symbol: str = "USDT", limit: int = 10, sortby: str = "date", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | ERC20 token symbol | WETH | True |
| to_symbol | str | Quoted currency. | USDT | True |
| limit | int | Last n days to query data | 10 | True |
| sortby | str | Key by which to sort data | date | True |
| ascend | bool | Flag to sort data ascending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Average bid and ask prices, spread for given crypto pair for chosen time period |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing an average bid and ask prices, average spread for given crypto pair for chosen

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_view.py#L346)]

```python
openbb.crypto.onchain.baas_chart(symbol: str = "WETH", to_symbol: str = "USDT", limit: int = 10, sortby: str = "date", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | ERC20 token symbol | WETH | True |
| to_symbol | str | Quoted currency. | USDT | True |
| limit | int | Last n days to query data | 10 | True |
| sortby | str | Key by which to sort data | date | True |
| ascend | bool | Flag to sort data ascending | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Average bid and ask prices, spread for given crypto pair for chosen time period |
---

</TabItem>
</Tabs>
