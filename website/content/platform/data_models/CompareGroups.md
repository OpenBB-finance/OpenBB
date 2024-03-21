---
title: "Compare Groups"
description: "Get company data grouped by sector, industry or country and display either performance or valuation metrics"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `CompareGroups` | `CompareGroupsQueryParams` | `CompareGroupsData` |

### Import Statement

```python
from openbb_core.provider.standard_models.compare_groups import (
CompareGroupsData,
CompareGroupsQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| group | str | The group to compare - i.e., 'sector', 'industry', 'country'. Choices vary by provider. | None | True |
| metric | str | The type of metrics to compare - i.e, 'valuation', 'performance'. Choices vary by provider. | None | True |
| provider | Literal['finviz'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

<TabItem value='finviz' label='finviz'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| group | str | The group to compare - i.e., 'sector', 'industry', 'country'. Choices vary by provider. | None | True |
| metric | str | The type of metrics to compare - i.e, 'valuation', 'performance'. Choices vary by provider. | None | True |
| provider | Literal['finviz'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name or label of the group. |
</TabItem>

<TabItem value='finviz' label='finviz'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name or label of the group. |
| stocks | int | The number of stocks in the group. |
| market_cap | int | The market cap of the group. |
| performance_1D | float | The performance in the last day, as a normalized percent. |
| performance_1W | float | The performance in the last week, as a normalized percent. |
| performance_1M | float | The performance in the last month, as a normalized percent. |
| performance_3M | float | The performance in the last quarter, as a normalized percent. |
| performance_6M | float | The performance in the last half year, as a normalized percent. |
| performance_1Y | float | The performance in the last year, as a normalized percent. |
| performance_YTD | float | The performance in the year to date, as a normalized percent. |
| dividend_yield | float | The dividend yield of the group, as a normalized percent. |
| pe | float | The P/E ratio of the group. |
| forward_pe | float | The forward P/E ratio of the group. |
| peg | float | The PEG ratio of the group. |
| eps_growth_past_5_years | float | The EPS growth of the group for the past 5 years, as a normalized percent. |
| eps_growth_next_5_years | float | The estimated EPS growth of the groupo for the next 5 years, as a normalized percent. |
| sales_growth_past_5_years | float | The sales growth of the group for the past 5 years, as a normalized percent. |
| float_short | float | The percent of the float shorted for the group, as a normalized value. |
| analyst_recommendation | float | The analyst consensus, on a scale of 1-5 where 1 is a buy and 5 is a sell. |
| volume | int | The trading volume. |
| volume_average | int | The 3-month average volume of the group. |
| volume_relative | float | The relative volume compared to the 3-month average volume. |
</TabItem>

</Tabs>

