---
title: "Analyst Search"
description: "Search for specific analysts and get their forecast track record"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `AnalystSearch` | `AnalystSearchQueryParams` | `AnalystSearchData` |

### Import Statement

```python
from openbb_core.provider.standard_models.analyst_search import (
AnalystSearchData,
AnalystSearchQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| analyst_name | str | A comma separated list of analyst names to bring back. Omitting will bring back all available analysts. | None | True |
| firm_name | str | A comma separated list of firm names to bring back. Omitting will bring back all available firms. | None | True |
| provider | Literal['benzinga'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| analyst_name | str | A comma separated list of analyst names to bring back. Omitting will bring back all available analysts. | None | True |
| firm_name | str | A comma separated list of firm names to bring back. Omitting will bring back all available firms. | None | True |
| provider | Literal['benzinga'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'benzinga' if there is no default. | benzinga | True |
| analyst_ids | Union[str, List[str]] | A comma separated list of analyst IDs to bring back. | None | True |
| firm_ids | Union[str, List[str]] | A comma separated list of firm IDs to bring back. | None | True |
| limit | int | Number of results returned. Limit 1000. | 100 | True |
| page | int | Page offset. For optimization, performance and technical reasons, page offsets are limited from 0 - 100000. Limit the query results by other parameters such as date. | 0 | True |
| fields | Union[str, List[str]] | Comma-separated list of fields to include in the response. See https://docs.benzinga.io/benzinga-apis/calendar/get-ratings to learn about the available fields. | None | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| last_updated | datetime | Date of the last update. |
| firm_name | str | Firm name of the analyst. |
| name_first | str | Analyst first name. |
| name_last | str | Analyst last name. |
| name_full | str | Analyst full name. |
</TabItem>

<TabItem value='benzinga' label='benzinga'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| last_updated | datetime | Date of the last update. |
| firm_name | str | Firm name of the analyst. |
| name_first | str | Analyst first name. |
| name_last | str | Analyst last name. |
| name_full | str | Analyst full name. |
| analyst_id | str | ID of the analyst. |
| firm_id | str | ID of the analyst firm. |
| smart_score | float | A weighted average of the total_ratings_percentile, overall_avg_return_percentile, and overall_success_rate |
| overall_success_rate | float | The percentage (normalized) of gain/loss ratings that resulted in a gain overall. |
| overall_avg_return_percentile | float | The percentile (normalized) of this analyst's overall average return per rating in comparison to other analysts' overall average returns per rating. |
| total_ratings_percentile | float | The percentile (normalized) of this analyst's total number of ratings in comparison to the total number of ratings published by all other analysts |
| total_ratings | int | Number of recommendations made by this analyst. |
| overall_gain_count | int | The number of ratings that have gained value since the date of recommendation |
| overall_loss_count | int | The number of ratings that have lost value since the date of recommendation |
| overall_average_return | float | The average percent (normalized) price difference per rating since the date of recommendation |
| overall_std_dev | float | The standard deviation in percent (normalized) price difference in the analyst's ratings since the date of recommendation |
| gain_count_1m | int | The number of ratings that have gained value over the last month |
| loss_count_1m | int | The number of ratings that have lost value over the last month |
| average_return_1m | float | The average percent (normalized) price difference per rating over the last month |
| std_dev_1m | float | The standard deviation in percent (normalized) price difference in the analyst's ratings over the last month |
| gain_count_3m | int | The number of ratings that have gained value over the last 3 months |
| loss_count_3m | int | The number of ratings that have lost value over the last 3 months |
| average_return_3m | float | The average percent (normalized) price difference per rating over the last 3 months |
| std_dev_3m | float | The standard deviation in percent (normalized) price difference in the analyst's ratings over the last 3 months |
| gain_count_6m | int | The number of ratings that have gained value over the last 6 months |
| loss_count_6m | int | The number of ratings that have lost value over the last 6 months |
| average_return_6m | float | The average percent (normalized) price difference per rating over the last 6 months |
| std_dev_6m | float | The standard deviation in percent (normalized) price difference in the analyst's ratings over the last 6 months |
| gain_count_9m | int | The number of ratings that have gained value over the last 9 months |
| loss_count_9m | int | The number of ratings that have lost value over the last 9 months |
| average_return_9m | float | The average percent (normalized) price difference per rating over the last 9 months |
| std_dev_9m | float | The standard deviation in percent (normalized) price difference in the analyst's ratings over the last 9 months |
| gain_count_1y | int | The number of ratings that have gained value over the last 1 year |
| loss_count_1y | int | The number of ratings that have lost value over the last 1 year |
| average_return_1y | float | The average percent (normalized) price difference per rating over the last 1 year |
| std_dev_1y | float | The standard deviation in percent (normalized) price difference in the analyst's ratings over the last 1 year |
| gain_count_2y | int | The number of ratings that have gained value over the last 2 years |
| loss_count_2y | int | The number of ratings that have lost value over the last 2 years |
| average_return_2y | float | The average percent (normalized) price difference per rating over the last 2 years |
| std_dev_2y | float | The standard deviation in percent (normalized) price difference in the analyst's ratings over the last 2 years |
| gain_count_3y | int | The number of ratings that have gained value over the last 3 years |
| loss_count_3y | int | The number of ratings that have lost value over the last 3 years |
| average_return_3y | float | The average percent (normalized) price difference per rating over the last 3 years |
| std_dev_3y | float | The standard deviation in percent (normalized) price difference in the analyst's ratings over the last 3 years |
</TabItem>

</Tabs>

