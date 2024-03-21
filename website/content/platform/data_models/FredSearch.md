---
title: "Fred Search"
description: "Search for FRED series or economic releases by ID or string"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `FredSearch` | `FredSearchQueryParams` | `FredSearchData` |

### Import Statement

```python
from openbb_core.provider.standard_models. import (
FredSearchData,
FredSearchQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | The search word(s). | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | The search word(s). | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| is_release | bool | Is release? If True, other search filter variables are ignored. If no query text or release_id is supplied, this defaults to True. | False | True |
| release_id | Union[int, str] | A specific release ID to target. | None | True |
| limit | int | The number of data entries to return. (1-1000) | None | True |
| offset | int, Ge(ge=0) | Offset the results in conjunction with limit. | 0 | True |
| filter_variable | Literal[None, 'frequency', 'units', 'seasonal_adjustment'] | Filter by an attribute. | None | True |
| filter_value | str | String value to filter the variable by. Used in conjunction with filter_variable. | None | True |
| tag_names | str | A semicolon delimited list of tag names that series match all of. Example: 'japan;imports' | None | True |
| exclude_tag_names | str | A semicolon delimited list of tag names that series match none of. Example: 'imports;services'. Requires that variable tag_names also be set to limit the number of matching series. | None | True |
| series_id | str | A FRED Series ID to return series group information for. This returns the required information to query for regional data. Not all series that are in FRED have geographical data. Entering a value for series_id will override all other parameters. Multiple series_ids can be separated by commas. | None | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| release_id | Union[int, str] | The release ID for queries. |
| series_id | str | The series ID for the item in the release. |
| name | str | The name of the release. |
| title | str | The title of the series. |
| observation_start | date | The date of the first observation in the series. |
| observation_end | date | The date of the last observation in the series. |
| frequency | str | The frequency of the data. |
| frequency_short | str | Short form of the data frequency. |
| units | str | The units of the data. |
| units_short | str | Short form of the data units. |
| seasonal_adjustment | str | The seasonal adjustment of the data. |
| seasonal_adjustment_short | str | Short form of the data seasonal adjustment. |
| last_updated | datetime | The datetime of the last update to the data. |
| notes | str | Description of the release. |
| press_release | bool | If the release is a press release. |
| url | str | URL to the release. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| release_id | Union[int, str] | The release ID for queries. |
| series_id | str | The series ID for the item in the release. |
| name | str | The name of the release. |
| title | str | The title of the series. |
| observation_start | date | The date of the first observation in the series. |
| observation_end | date | The date of the last observation in the series. |
| frequency | str | The frequency of the data. |
| frequency_short | str | Short form of the data frequency. |
| units | str | The units of the data. |
| units_short | str | Short form of the data units. |
| seasonal_adjustment | str | The seasonal adjustment of the data. |
| seasonal_adjustment_short | str | Short form of the data seasonal adjustment. |
| last_updated | datetime | The datetime of the last update to the data. |
| notes | str | Description of the release. |
| press_release | bool | If the release is a press release. |
| url | str | URL to the release. |
| popularity | int | Popularity of the series |
| group_popularity | int | Group popularity of the release |
| region_type | str | The region type of the series. |
| series_group | Union[int, str] | The series group ID of the series. This value is used to query for regional data. |
</TabItem>

</Tabs>

