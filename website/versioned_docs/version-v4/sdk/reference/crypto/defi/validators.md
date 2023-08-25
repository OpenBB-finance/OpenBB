---
title: validators
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# validators

<Tabs>
<TabItem value="model" label="Model" default>

Get information about terra validators [Source: https://fcd.terra.dev/swagger]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_model.py#L155)]

```python
openbb.crypto.defi.validators(sortby: str = "votingPower", ascend: bool = True)
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | terra validators details |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing information about terra validators [Source: https://fcd.terra.dev/swagger]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_view.py#L64)]

```python
openbb.crypto.defi.validators_chart(limit: int = 10, sortby: str = "votingPower", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 10 | True |
| sortby | str | Key by which to sort data. Choose from:<br/>validatorName, tokensAmount, votingPower, commissionRate, status, uptime | votingPower | True |
| ascend | bool | Flag to sort data descending | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>