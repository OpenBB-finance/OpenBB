---
title: "long_term_interest_rate"
description: "Long-term interest rates refer to government bonds maturing in ten years"
keywords:
- economy
- long_term_interest_rate
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/long_term_interest_rate - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Long-term interest rates refer to government bonds maturing in ten years.
Rates are mainly determined by the price charged by the lender, the risk from the borrower and the
fall in the capital value. Long-term interest rates are generally averages of daily rates,
measured as a percentage. These interest rates are implied by the prices at which the government bonds are
traded on financial markets, not the interest rates at which the loans were issued.
In all cases, they refer to bonds whose capital repayment is guaranteed by governments.
Long-term interest rates are one of the determinants of business investment.
Low long-term interest rates encourage investment in new equipment and high interest rates discourage it.
Investment is, in turn, a major source of economic growth.


Examples
--------

```python
from openbb import obb
obb.economy.long_term_interest_rate(provider='oecd')
obb.economy.long_term_interest_rate(country=all, frequency=quarterly, provider='oecd')
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
    results : LTIR
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

