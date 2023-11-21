---
title: forecast
description: Forecasted GDP Data
keywords:
- economy
- gdp
- forecast
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /gdp/forecast - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Forecasted GDP Data.

```python wordwrap
obb.economy.gdp.forecast(period: Literal[str] = annual, start_date: Union[date, str] = None, end_date: Union[date, str] = None, type: Literal[str] = real, provider: Literal[str] = oecd)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| period | Literal['quarter', 'annual'] | Time period of the data to return. Units for nominal GDP period. Either quarter or annual. | annual | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| type | Literal['nominal', 'real'] | Type of GDP to get forecast of. Either nominal or real. | real | True |
| provider | Literal['oecd'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'oecd' if there is no default. | oecd | True |
</TabItem>

<TabItem value='oecd' label='oecd'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| period | Literal['quarter', 'annual'] | Time period of the data to return. Units for nominal GDP period. Either quarter or annual. | annual | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| type | Literal['nominal', 'real'] | Type of GDP to get forecast of. Either nominal or real. | real | True |
| provider | Literal['oecd'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'oecd' if there is no default. | oecd | True |
| country | Literal['argentina', 'asia', 'australia', 'austria', 'belgium', 'brazil', 'bulgaria', 'canada', 'chile', 'china', 'colombia', 'costa_rica', 'croatia', 'czech_republic', 'denmark', 'estonia', 'euro_area_17', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'india', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'mexico', 'netherlands', 'new_zealand', 'non-oecd', 'norway', 'oecd_total', 'peru', 'poland', 'portugal', 'romania', 'russia', 'slovak_republic', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states', 'world'] | Country to get GDP for. | united_states | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[GdpForecast]
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

