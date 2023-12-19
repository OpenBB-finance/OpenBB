---
title: lt
description: Docusaurus page containing OpenBBTerminal's onchain lt model and view
  that depict trades happening on Decentralized Exchanges - aggregated per DEX or
  time. Also includes code snippets, parameter details, and return values.
keywords:
- onchain
- lt model
- Decentralized Exchanges
- DEX
- lt view
- onchain trading
- trades aggregation
- code snippets
- parameter details
- return values
- Bitcoin
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.lt - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get trades on Decentralized Exchanges aggregated by DEX [Source: https://graphql.bitquery.io/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L266)]

```python
openbb.crypto.onchain.lt(trade_amount_currency: str = "USD", limit: int = 90, sortby: str = "tradeAmount", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| trade_amount_currency | str | Currency of displayed trade amount. Default: USD | USD | True |
| limit | int | Last n days to query data. Maximum 365 (bigger numbers can cause timeouts<br/>on server side) | 90 | True |
| sortby | str | Key by which to sort data | tradeAmount | True |
| ascend | bool | Flag to sort data ascending | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Trades on Decentralized Exchanges aggregated by DEX |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing Trades on Decentralized Exchanges aggregated by DEX or Month

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_view.py#L22)]

```python
openbb.crypto.onchain.lt_chart(trade_amount_currency: str = "USD", kind: str = "dex", limit: int = 20, days: int = 90, sortby: str = "tradeAmount", ascend: bool = True, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| kind | str | Aggregate trades by dex or time | dex | True |
| trade_amount_currency | str | Currency of displayed trade amount. Default: USD | USD | True |
| limit | int | Number of records to display | 20 | True |
| sortby | str | Key by which to sort data | tradeAmount | True |
| ascend | bool | Flag to sort data ascending | True | True |
| days | int | Last n days to query data. Maximum 365 (bigger numbers can cause timeouts<br/>on server side) | 90 | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
