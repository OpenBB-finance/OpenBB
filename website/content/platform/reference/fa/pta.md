---
title: pta
description: This is documentation on how to obtain Price Target data using 'pta'.
  This function allows querying by symbol and provider. It can return a variety of
  fields including analyst information, news related to the target price, grades and
  more. The data can be retrieved from a standard or 'fmp' provider option.
keywords:
- Price Target
- pta
- fmp
- Price Target data
- Python
- Documentation
- Parameters
- Grading company
- Analyst name
- Analyst company
- News URL
- News Title
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fa.pta - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Price Target. Price target data.

```python wordwrap
pta(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| with_grade | bool | Include upgrades and downgrades in the response. | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[PriceTarget]
        Serializable results.

    provider : Optional[Literal['fmp']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| published_date | datetime | Published date of the price target. |
| news_url | str | News URL of the price target. |
| news_title | str | News title of the price target. |
| analyst_name | str | Analyst name. |
| analyst_company | str | Analyst company. |
| price_target | float | Price target. |
| adj_price_target | float | Adjusted price target. |
| price_when_posted | float | Price when posted. |
| news_publisher | str | News publisher of the price target. |
| news_base_url | str | News base URL of the price target. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| published_date | datetime | Published date of the price target. |
| news_url | str | News URL of the price target. |
| news_title | str | News title of the price target. |
| analyst_name | str | Analyst name. |
| analyst_company | str | Analyst company. |
| price_target | float | Price target. |
| adj_price_target | float | Adjusted price target. |
| price_when_posted | float | Price when posted. |
| news_publisher | str | News publisher of the price target. |
| news_base_url | str | News base URL of the price target. |
| new_grade | str | New grade |
| previous_grade | str | Previous grade |
| grading_company | str | Grading company |
</TabItem>

</Tabs>
