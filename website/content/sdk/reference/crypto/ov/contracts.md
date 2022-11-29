---
title: contracts
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# contracts

<Tabs>
<TabItem value="model" label="Model" default>

Gets all contract addresses for given platform [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_model.py#L400)]

```python
openbb.crypto.ov.contracts(platform_id: str = "eth-ethereum", sortby: str = "active", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| platform_id | str | Blockchain platform like eth-ethereum | eth-ethereum | True |
| sortby | str | Key by which to sort data | active | True |
| ascend | bool | Flag to sort data ascend | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | id, type, active |
---



</TabItem>
<TabItem value="view" label="Chart">

Gets all contract addresses for given platform. [Source: CoinPaprika]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_view.py#L349)]

```python
openbb.crypto.ov.contracts_chart(symbol: str, sortby: str = "active", ascend: bool = True, limit: int = 15, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| platform | str | Blockchain platform like eth-ethereum | None | True |
| limit | int | Number of records to display | 15 | True |
| sortby | str | Key by which to sort data | active | True |
| ascend | bool | Flag to sort data ascending | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>