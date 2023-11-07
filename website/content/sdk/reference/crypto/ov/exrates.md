---
title: exrates
description: Explanation and source code of 'exrates', a feature from OpenBB-finance
  which fetches a list of cryptocurrency, fiat, and commodity exchange rates from
  the CoinGecko API. This page includes how to use the function, its parameters, and
  its returns.
keywords:
- exrates
- OpenBB-finance
- CoinGecko API
- cryptocurrency
- exchange rates
- crypto
- fiats
- commodity
- parameters
- returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.ov.exrates - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get list of crypto, fiats, commodity exchange rates from CoinGecko API [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_model.py#L423)]

```python
openbb.crypto.ov.exrates(sortby: str = "Name", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key by which to sort data | Name | True |
| ascend | bool | Flag to sort data ascending | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Index, Name, Unit, Value, Type |
---

</TabItem>
<TabItem value="view" label="Chart">

Shows  list of crypto, fiats, commodity exchange rates. [Source: CoinGecko]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L200)]

```python
openbb.crypto.ov.exrates_chart(sortby: str = "Name", ascend: bool = False, limit: int = 15, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | 15 | True |
| sortby | str | Key by which to sort data | Name | True |
| ascend | bool | Flag to sort data ascending | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
