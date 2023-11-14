---
title: nominal
description: Learn how to get nominal GDP data using different parameters such as
  units of measurement, start and end dates, data provider, and country. Explore the
  returned results, provider information, warnings, and metadata. Understand the structure
  of the data including the date and value of the GDP.
keywords:
- Nominal GDP Data
- get nominal GDP
- units of measurement
- start date
- end date
- data provider
- country
- GDP value
- date of the data
---



<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Nominal GDP Data.

```python wordwrap
obb.economy.gdp.nominal(units: Literal[str] = usd, start_date: Union[date, str] = None, end_date: Union[date, str] = None, provider: Literal[str] = oecd)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| units | Literal['usd', 'usd_cap'] | The unit of measurement for the data. Units to get nominal GDP in. Either usd or usd_cap indicating per capita. | usd | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['oecd'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'oecd' if there is no default. | oecd | True |
</TabItem>

<TabItem value='oecd' label='oecd'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| units | Literal['usd', 'usd_cap'] | The unit of measurement for the data. Units to get nominal GDP in. Either usd or usd_cap indicating per capita. | usd | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['oecd'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'oecd' if there is no default. | oecd | True |
| country | Literal['australia', 'austria', 'belgium', 'brazil', 'canada', 'chile', 'colombia', 'costa_rica', 'czech_republic', 'denmark', 'estonia', 'euro_area', 'european_union', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'mexico', 'netherlands', 'new_zealand', 'norway', 'poland', 'portugal', 'russia', 'slovak_republic', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states'] | Country to get GDP for. | united_states | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[GdpNominal]
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

