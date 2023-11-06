---
title: cbpairs
description: This page provides in-depth information on how to use different functions
  to get a list of available trading pairs or visualize it in a chart form with source
  code supplied from OpenBB-finance/OpenBBTerminal project on GitHub.
keywords:
- OpenBB-finance
- GitHub
- cryptocurrency
- trading pairs
- coinbase
- model
- view
- charts
- visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.cbpairs - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get a list of available currency pairs for trading. [Source: Coinbase]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinbase_model.py#L24)]

```python
openbb.crypto.ov.cbpairs(limit: int = 50, sortby: str = "quote_increment", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Top n of pairs | 50 | True |
| sortby | str | Key to sortby data | quote_increment | True |
| ascend | bool | Sort descending flag | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Available trading pairs on Coinbase |
---

</TabItem>
<TabItem value="view" label="Chart">

Displays a list of available currency pairs for trading. [Source: Coinbase]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinbase_view.py#L19)]

```python
openbb.crypto.ov.cbpairs_chart(limit: int = 20, sortby: str = "quote_increment", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Top n of pairs | 20 | True |
| sortby | str | Key to sortby data | quote_increment | True |
| ascend | bool | Sort ascending flag | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
