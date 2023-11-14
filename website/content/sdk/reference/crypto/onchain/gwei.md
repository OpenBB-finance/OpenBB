---
title: gwei
description: This documentation page details the 'gwei' functionality of OpenBB's
  crypto onchain operations. It contains code snippets and function descriptions for
  retrieving Ethereum gas fees data, along with export methods for the same.
keywords:
- crypto onchain operations
- gwei
- Ethereum gas fees data
- data export
- Source Code
- function documentation
- onchain data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.gwei - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns the most recent Ethereum gas fees in gwei

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethgasstation_model.py#L13)]

```python
openbb.crypto.onchain.gwei()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | four gas fees and durations<br/>    (fees for slow, average, fast and<br/>    fastest transactions in gwei and<br/>    its average durations in seconds) |
---

</TabItem>
<TabItem value="view" label="Chart">

Current gwei fees

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethgasstation_view.py#L14)]

```python
openbb.crypto.onchain.gwei_chart(export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
