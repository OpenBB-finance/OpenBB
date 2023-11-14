---
title: real
description: Learn about Real GDP Data and how to access it using the provided parameters.
  Find detailed descriptions of the available parameters and the data returned. Understand
  the structure of the returns and explore the data attributes.
keywords:
- Real GDP Data
- parameters
- units
- start date
- end date
- provider
- country
- returns
- results
- GdpReal
- warnings
- chart
- metadata
- data
- date
- value
- documentation
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Real GDP Data.

```python wordwrap
obb.economy.gdp.real(units: Literal[str] = yoy, start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = oecd)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| units | Literal['idx', 'qoq', 'yoy'] | The unit of measurement for the data. Either idx (indicating 2015=100), qoq (previous period) or yoy (same period, previous year).) | yoy | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['oecd'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'oecd' if there is no default. | oecd | True |
</TabItem>

<TabItem value='oecd' label='oecd'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| units | Literal['idx', 'qoq', 'yoy'] | The unit of measurement for the data. Either idx (indicating 2015=100), qoq (previous period) or yoy (same period, previous year).) | yoy | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['oecd'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'oecd' if there is no default. | oecd | True |
| country | Literal['G20', 'G7', 'argentina', 'australia', 'austria', 'belgium', 'brazil', 'bulgaria', 'canada', 'chile', 'china', 'colombia', 'costa_rica', 'croatia', 'czech_republic', 'denmark', 'estonia', 'euro_area_19', 'europe', 'european_union_27', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'india', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'mexico', 'netherlands', 'new_zealand', 'norway', 'oecd_total', 'poland', 'portugal', 'romania', 'russia', 'saudi_arabia', 'slovak_republic', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states'] | Country to get GDP for. | united_states | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[GdpReal]
        Serializable results.

    provider : Optional[Literal['oecd']]
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
| value | float | Nominal GDP value on the date. |
</TabItem>

</Tabs>

