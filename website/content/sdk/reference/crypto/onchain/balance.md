---
title: balance
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# balance

<Tabs>
<TabItem value="model" label="Model" default>

Get info about tokens on you ethereum blockchain balance. Eth balance, balance of all tokens which

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethplorer_model.py#L196)]

```python
openbb.crypto.onchain.balance(address: str, sortby: str = "index", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | Blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699 | None | False |
| sortby | str | Key to sort by. | index | True |
| ascend | str | Sort in descending order. | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with list of tokens and their balances. |
---



</TabItem>
<TabItem value="view" label="Chart">

Display info about tokens for given ethereum blockchain balance e.g. ETH balance,

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethplorer_view.py#L21)]

```python
openbb.crypto.onchain.balance_chart(address: str, limit: int = 15, sortby: str = "index", ascend: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | Ethereum balance. | None | False |
| limit | int | Limit of transactions. Maximum 100 | 15 | True |
| sortby | str | Key to sort by. | index | True |
| ascend | str | Sort in descending order. | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>