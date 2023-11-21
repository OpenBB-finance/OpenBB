---
title: dvcp
description: This documentation page contains information about dvcp, a function from
  the OpenBB framework that provides data about the daily volume of a specific cryptocurrency
  pair. Both the data model and a chart view are presented. The documentation includes
  source code links, detailed information about parameters and returned data.
keywords:
- dvcp
- cryptocurrency
- daily volume
- ERC20 token
- data model
- chart view
- parameters
- returned data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.dvcp - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get daily volume for given pair [Source: https://graphql.bitquery.io/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L400)]

```python
openbb.crypto.onchain.dvcp(limit: int = 100, symbol: str = "UNI", to_symbol: str = "USDT", sortby: str = "date", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Last n days to query data | 100 | True |
| symbol | str | ERC20 token symbol | UNI | True |
| to_symbol | str | Quote currency. | USDT | True |
| sortby | str | Key by which to sort data | date | True |
| ascend | bool | Flag to sort data ascending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Daily volume for given pair |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing daily volume for given pair

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_view.py#L87)]

```python
openbb.crypto.onchain.dvcp_chart(symbol: str = "WBTC", to_symbol: str = "USDT", limit: int = 20, sortby: str = "date", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | ERC20 token symbol or address | WBTC | True |
| to_symbol | str | Quote currency. | USDT | True |
| limit | int | Number of records to display | 20 | True |
| sortby | str | Key by which to sort data | date | True |
| ascend | bool | Flag to sort data ascending | True | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Token volume on different decentralized exchanges |
---

</TabItem>
</Tabs>
