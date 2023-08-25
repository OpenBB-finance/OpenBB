---
title: prices
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# prices

<Tabs>
<TabItem value="model" label="Model" default>

Get token historical prices with volume and market cap, and average price. [Source: Ethplorer]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethplorer_model.py#L545)]

```python
openbb.crypto.onchain.prices(address: str, sortby: str = "date", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | Token e.g. 0xf3db5fa2c66b7af3eb0c0b782510816cbe4813b8 | None | False |
| sortby | str | Key to sort by. | date | True |
| ascend | str | Sort in descending order. | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with token historical prices. |
---



</TabItem>
<TabItem value="view" label="Chart">

Display token historical prices with volume and market cap, and average price.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethplorer_view.py#L334)]

```python
openbb.crypto.onchain.prices_chart(address: str, limit: int = 30, sortby: str = "date", ascend: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 | None | False |
| limit | int | Limit of transactions. Maximum 100 | 30 | True |
| sortby | str | Key to sort by. | date | True |
| ascend | str | Sort in descending order. | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>