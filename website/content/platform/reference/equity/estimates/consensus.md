---
title: "consensus"
description: "Learn how to access and use the Price Target Consensus functionality  in your application. Explore the available parameters and understand the returned  data structure."
keywords:
- Price target consensus data
- equity estimates consensus
- symbol parameter
- provider parameter
- results attribute
- provider attribute
- warnings attribute
- chart attribute
- metadata attribute
- data table
- target_high column
- target_low column
- target_consensus column
- target_median column
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/estimates/consensus - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get consensus price target and recommendation.


Examples
--------

```python
from openbb import obb
obb.equity.estimates.consensus(symbol='AAPL', provider='fmp')
obb.equity.estimates.consensus(symbol='AAPL,MSFT', provider='yfinance')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): tmx, yfinance. |  | False |
| provider | Literal['fmp', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): tmx, yfinance. |  | False |
| provider | Literal['fmp', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): tmx, yfinance. |  | False |
| provider | Literal['fmp', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): tmx, yfinance. |  | False |
| provider | Literal['fmp', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : PriceTargetConsensus
        Serializable results.
    provider : Literal['fmp', 'tmx', 'yfinance']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| target_high | float | High target of the price target consensus. |
| target_low | float | Low target of the price target consensus. |
| target_consensus | float | Consensus target of the price target consensus. |
| target_median | float | Median target of the price target consensus. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| target_high | float | High target of the price target consensus. |
| target_low | float | Low target of the price target consensus. |
| target_consensus | float | Consensus target of the price target consensus. |
| target_median | float | Median target of the price target consensus. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| target_high | float | High target of the price target consensus. |
| target_low | float | Low target of the price target consensus. |
| target_consensus | float | Consensus target of the price target consensus. |
| target_median | float | Median target of the price target consensus. |
| target_upside | float | Percent of upside, as a normalized percent. |
| total_analysts | int | Total number of analyst. |
| buy_ratings | int | Number of buy ratings. |
| sell_ratings | int | Number of sell ratings. |
| hold_ratings | int | Number of hold ratings. |
| consensus_action | str | Consensus action. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| target_high | float | High target of the price target consensus. |
| target_low | float | Low target of the price target consensus. |
| target_consensus | float | Consensus target of the price target consensus. |
| target_median | float | Median target of the price target consensus. |
| recommendation | str | Recommendation - buy, sell, etc. |
| recommendation_mean | float | Mean recommendation score where 1 is strong buy and 5 is strong sell. |
| number_of_analysts | int | Number of analysts providing opinions. |
| current_price | float | Current price of the stock. |
| currency | str | Currency the stock is priced in. |
</TabItem>

</Tabs>

