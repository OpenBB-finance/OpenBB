---
title: cpi
description: Get Consumer Price Index (CPI) data for various countries and calculate
  inflation measurements. This economic indicator provides insights into the growth
  rate of prices on a monthly, quarterly, and annual basis. Harmonized CPI data is
  also available. Specify the start and end dates for the desired data range. The
  data provider and metadata information are included in the results.
keywords:
- Consumer Price Index (CPI) Data
- CPI data
- CPI calculation
- inflation measurement
- economic indicator
- country-wise CPI data
- growth rate
- monthly CPI
- quarterly CPI
- annual CPI
- harmonized CPI
- start date
- end date
- data provider
- metadata info
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Consumer Price Index (CPI) Data.

```python wordwrap
obb.economy.cpi(countries: List[Literal[str]], units: Literal[str] = growth_same, frequency: Literal[str] = monthly, harmonized: bool = False, start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fred)
```

---

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

---

## Returns

```python wordwrap
OBBject
    results : List[ConsumerPriceIndex]
        Serializable results.

    provider : Optional[Literal['fred']]
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
| date | date | The date of the data. |
</TabItem>

</Tabs>

