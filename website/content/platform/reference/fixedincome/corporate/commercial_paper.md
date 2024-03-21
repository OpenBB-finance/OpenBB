---
title: "commercial_paper"
description: "Learn about commercial paper, a form of short-term promissory notes issued  primarily by corporations. Discover how it can help raise cash for current transactions  and serve as a lower-cost alternative to bank loans. Explore the parameters and  data returned by the commercial paper API endpoint."
keywords:
- commercial paper
- short-term promissory notes
- corporations
- raise cash
- lower-cost alternative
- start_date
- end_date
- maturity
- category
- grade
- provider
- results
- warnings
- chart
- metadata
- data
- date
- rate
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome/corporate/commercial_paper - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Commercial Paper.

Commercial paper (CP) consists of short-term, promissory notes issued primarily by corporations.
Maturities range up to 270 days but average about 30 days.
Many companies use CP to raise cash needed for current transactions,
and many find it to be a lower-cost alternative to bank loans.


Examples
--------

```python
from openbb import obb
obb.fixedincome.corporate.commercial_paper(provider='fred')
obb.fixedincome.corporate.commercial_paper(maturity='15d', provider='fred')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| maturity | Literal['overnight', '7d', '15d', '30d', '60d', '90d'] | The maturity. | 30d | True |
| category | Literal['asset_backed', 'financial', 'nonfinancial'] | The category. | financial | True |
| grade | Literal['aa', 'a2_p2'] | The grade. | aa | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| maturity | Literal['overnight', '7d', '15d', '30d', '60d', '90d'] | The maturity. | 30d | True |
| category | Literal['asset_backed', 'financial', 'nonfinancial'] | The category. | financial | True |
| grade | Literal['aa', 'a2_p2'] | The grade. | aa | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : CommercialPaper
        Serializable results.
    provider : Literal['fred']
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
| rate | float | Commercial Paper Rate. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | Commercial Paper Rate. |
</TabItem>

</Tabs>

