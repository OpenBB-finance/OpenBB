---
title: "unemployment"
description: "Global unemployment data"
keywords:
- economy
- unemployment
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/unemployment - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Global unemployment data.


Examples
--------

```python
from openbb import obb
obb.economy.unemployment(provider='oecd')
obb.economy.unemployment(country=all, frequency=quarterly, provider='oecd')
# Demographics for the statistics are selected with the `age` parameter.
obb.economy.unemployment(country=all, frequency=quarterly, age=25-54, provider='oecd')
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
| country | Literal['colombia', 'new_zealand', 'united_kingdom', 'italy', 'luxembourg', 'euro_area19', 'sweden', 'oecd', 'south_africa', 'denmark', 'canada', 'switzerland', 'slovakia', 'hungary', 'portugal', 'spain', 'france', 'czech_republic', 'costa_rica', 'japan', 'slovenia', 'russia', 'austria', 'latvia', 'netherlands', 'israel', 'iceland', 'united_states', 'ireland', 'mexico', 'germany', 'greece', 'turkey', 'australia', 'poland', 'south_korea', 'chile', 'finland', 'european_union27_2020', 'norway', 'lithuania', 'euro_area20', 'estonia', 'belgium', 'brazil', 'indonesia', 'all'] | Country to get GDP for. | united_states | True |
| sex | Literal['total', 'male', 'female'] | Sex to get unemployment for. | total | True |
| frequency | Literal['monthly', 'quarterly', 'annual'] | Frequency to get unemployment for. | monthly | True |
| age | Literal['total', '15-24', '15-64', '25-54', '55-64'] | Age group to get unemployment for. Total indicates 15 years or over | total | True |
| seasonal_adjustment | bool | Whether to get seasonally adjusted unemployment. Defaults to False. | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : Unemployment
        Serializable results.
    provider : Literal['oecd']
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
| value | float | Unemployment rate (given as a whole number, i.e 10=10%) |
| country | str | Country for which unemployment rate is given |
</TabItem>

<TabItem value='oecd' label='oecd'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| value | float | Unemployment rate (given as a whole number, i.e 10=10%) |
| country | str | Country for which unemployment rate is given |
</TabItem>

</Tabs>

