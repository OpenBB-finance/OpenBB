---
title: cpi
description: This page offers detailed API documentation for retrieving Consumer Price
  Index (CPI) from various countries using the Python 'cpi' function. The function
  parameters, return objects and corresponding data fields are thoroughly explained.
keywords:
- cpi
- Consumer Price Index
- python wordwrap
- parameters
- countries
- units
- frequency
- harmonized
- start_date
- end_date
- provider
- returns
- results
- warnings
- chart
- metadata
- data
- date
- value
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="cpi - Economy - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cpi

CPI. Consumer Price Index.

```python wordwrap
cpi(countries: List[Literal[str]], units: Literal[str] = growth_same, frequency: Literal[str] = monthly, harmonized: bool = False, start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = fred)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | List[Literal['australia', 'austria', 'belgium', 'brazil', 'bulgaria', 'canada', 'chile', 'china', 'croatia', 'cyprus', 'czech_republic', 'denmark', 'estonia', 'euro_area', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'india', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'malta', 'mexico', 'netherlands', 'new_zealand', 'norway', 'poland', 'portugal', 'romania', 'russian_federation', 'slovak_republic', 'slovakia', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states']] | The country or countries to get data. |  | False |
| units | Literal['growth_previous', 'growth_same', 'index_2015'] | The data units. | growth_same | True |
| frequency | Literal['monthly', 'quarter', 'annual'] | The data time frequency. | monthly | True |
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
    results : List[CPI]
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
| value | float | CPI value on the date. |
</TabItem>

</Tabs>
