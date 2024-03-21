---
title: "short_term_interest_rate"
description: "Short-term interest rates are the rates at which short-term borrowings are effected between
financial institutions or the rate at which short-term government paper is issued or traded in the market"
keywords:
- economy
- short_term_interest_rate
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/short_term_interest_rate - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Short-term interest rates are the rates at which short-term borrowings are effected between
financial institutions or the rate at which short-term government paper is issued or traded in the market.
Short-term interest rates are generally averages of daily rates, measured as a percentage.
Short-term interest rates are based on three-month money market rates where available.
Typical standardised names are "money market rate" and "treasury bill rate".


Examples
--------

```python
from openbb import obb
obb.economy.short_term_interest_rate(provider='oecd')
obb.economy.short_term_interest_rate(country=all, frequency=quarterly, provider='oecd')
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
| country | Literal['belgium', 'ireland', 'mexico', 'indonesia', 'new_zealand', 'japan', 'united_kingdom', 'france', 'chile', 'canada', 'netherlands', 'united_states', 'south_korea', 'norway', 'austria', 'south_africa', 'denmark', 'switzerland', 'hungary', 'luxembourg', 'australia', 'germany', 'sweden', 'iceland', 'turkey', 'greece', 'israel', 'czech_republic', 'latvia', 'slovenia', 'poland', 'estonia', 'lithuania', 'portugal', 'costa_rica', 'slovakia', 'finland', 'spain', 'russia', 'euro_area19', 'colombia', 'italy', 'india', 'china', 'croatia', 'all'] | Country to get GDP for. | united_states | True |
| frequency | Literal['monthly', 'quarterly', 'annual'] | Frequency to get interest rate for for. | monthly | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : STIR
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
| value | float | Interest rate (given as a whole number, i.e 10=10%) |
| country | str | Country for which interest rate is given |
</TabItem>

<TabItem value='oecd' label='oecd'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| value | float | Interest rate (given as a whole number, i.e 10=10%) |
| country | str | Country for which interest rate is given |
</TabItem>

</Tabs>

