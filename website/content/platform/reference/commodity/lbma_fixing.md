---
title: "lbma_fixing"
description: "Daily LBMA Fixing Prices in USD/EUR/GBP"
keywords:
- commodity
- lbma_fixing
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="commodity/lbma_fixing - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Daily LBMA Fixing Prices in USD/EUR/GBP.


Examples
--------

```python
from openbb import obb
obb.commodity.lbma_fixing(provider='nasdaq')
# Get the daily LBMA fixing prices for silver in 2023.
obb.commodity.lbma_fixing(asset='silver', start_date='2023-01-01', end_date='2023-12-31', transform='rdiff', collapse='monthly', provider='nasdaq')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| asset | Literal['gold', 'silver'] | The metal to get price fixing rates for. | gold | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| transform | Literal['diff', 'rdiff', 'cumul', 'normalize'] | Transform the data as difference, percent change, cumulative, or normalize. | None | True |
| collapse | Literal['daily', 'weekly', 'monthly', 'quarterly', 'annual'] | Collapse the frequency of the time series. | None | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| asset | Literal['gold', 'silver'] | The metal to get price fixing rates for. | gold | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| transform | Literal['diff', 'rdiff', 'cumul', 'normalize'] | Transform the data as difference, percent change, cumulative, or normalize. | None | True |
| collapse | Literal['daily', 'weekly', 'monthly', 'quarterly', 'annual'] | Collapse the frequency of the time series. | None | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : LbmaFixing
        Serializable results.
    provider : Literal['nasdaq']
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
| date | date | The date of the data. |
| usd_am | float | AM fixing price in USD. |
| usd_pm | float | PM fixing price in USD. |
| gbp_am | float | AM fixing price in GBP. |
| gbp_pm | float | PM fixing price in GBP. |
| euro_am | float | AM fixing price in EUR. |
| euro_pm | float | PM fixing price in EUR. |
| usd | float | Daily fixing price in USD. |
| gbp | float | Daily fixing price in GBP. |
| eur | float | Daily fixing price in EUR. |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| usd_am | float | AM fixing price in USD. |
| usd_pm | float | PM fixing price in USD. |
| gbp_am | float | AM fixing price in GBP. |
| gbp_pm | float | PM fixing price in GBP. |
| euro_am | float | AM fixing price in EUR. |
| euro_pm | float | PM fixing price in EUR. |
| usd | float | Daily fixing price in USD. |
| gbp | float | Daily fixing price in GBP. |
| eur | float | Daily fixing price in EUR. |
</TabItem>

</Tabs>

