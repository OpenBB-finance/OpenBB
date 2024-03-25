---
title: "CLI"
description: "The composite leading indicator (CLI) is designed to provide early signals of turning points
in business cycles showing fluctuation of the economic activity around its long term potential level"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `CLI` | `CLIQueryParams` | `CLIData` |

### Import Statement

```python
from openbb_core.provider.standard_models.composite_leading_indicator import (
CLIData,
CLIQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['oecd'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'oecd' if there is no default. | oecd | True |
</TabItem>

<TabItem value='oecd' label='oecd'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['oecd'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'oecd' if there is no default. | oecd | True |
| country | Literal['united_states', 'united_kingdom', 'japan', 'mexico', 'indonesia', 'australia', 'brazil', 'canada', 'italy', 'germany', 'turkey', 'france', 'south_africa', 'south_korea', 'spain', 'india', 'china', 'g7', 'g20', 'all'] | Country to get GDP for. | united_states | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| value | float | CLI value |
| country | str | Country for which CLI is given |
</TabItem>

<TabItem value='oecd' label='oecd'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| value | float | CLI value |
| country | str | Country for which CLI is given |
</TabItem>

</Tabs>

