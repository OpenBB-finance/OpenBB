---
title: Consumer Price Index (CPI) Data
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `ConsumerPriceIndex` | `ConsumerPriceIndexQueryParams` | `ConsumerPriceIndexData` |

### Import Statement

```python
from openbb_core.provider.standard_models.cpi import (
ConsumerPriceIndexData,
ConsumerPriceIndexQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | List[Literal['australia', 'austria', 'belgium', 'brazil', 'bulgaria', 'canada', 'chile', 'china', 'croatia', 'cyprus', 'czech_republic', 'denmark', 'estonia', 'euro_area', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'india', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'malta', 'mexico', 'netherlands', 'new_zealand', 'norway', 'poland', 'portugal', 'romania', 'russian_federation', 'slovak_republic', 'slovakia', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states']] | The country or countries to get data. |  | False |
| units | Literal['growth_previous', 'growth_same', 'index_2015'] | The unit of measurement for the data.
    Options:
    - `growth_previous`: growth from the previous period
    - `growth_same`: growth from the same period in the previous year
    - `index_2015`: index with base year 2015. | growth_same | True |
| frequency | Literal['monthly', 'quarter', 'annual'] | The frequency of the data.
    Options: `monthly`, `quarter`, and `annual`. | monthly | True |
| harmonized | bool | Whether you wish to obtain harmonized data. | False | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
</TabItem>

</Tabs>
