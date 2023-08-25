---
title: derivatives
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# derivatives

<Tabs>
<TabItem value="model" label="Model" default>

Get list of crypto derivatives from CoinGecko API [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_model.py#L375)]

```python
openbb.crypto.ov.derivatives(sortby: str = "Rank", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key by which to sort data | Rank | True |
| ascend | bool | Flag to sort data descending | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread,<br/>Funding_Rate, Volume_24h, |
---



</TabItem>
<TabItem value="view" label="Chart">

Shows  list of crypto derivatives. [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L645)]

```python
openbb.crypto.ov.derivatives_chart(sortby: str = "Rank", ascend: bool = False, limit: int = 15, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 15 | True |
| sortby | str | Key by which to sort data | Rank | True |
| ascend | bool | Flag to sort data descending | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>