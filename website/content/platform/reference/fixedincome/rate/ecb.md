---
title: "ecb"
description: "Learn about the key interest rates set by the European Central Bank (ECB)  for the Euro area. Explore the Python API for accessing European Central Bank interest  rate data and understand the available parameters to customize your queries."
keywords:
- European Central Bank interest rates
- ECB key interest rates
- ECB refinancing operations
- deposit facility rate
- marginal lending facility rate
- Python OBB fixed income API
- start date parameter
- end date parameter
- interest rate type parameter
- provider parameter
- European Central Bank Interest Rates data
- European Central Bank Interest Rates API
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome/rate/ecb - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

European Central Bank Interest Rates.

The Governing Council of the ECB sets the key interest rates for the euro area:

- The interest rate on the main refinancing operations (MRO), which provide
the bulk of liquidity to the banking system.
- The rate on the deposit facility, which banks may use to make overnight deposits with the Eurosystem.
- The rate on the marginal lending facility, which offers overnight credit to banks from the Eurosystem.


Examples
--------

```python
from openbb import obb
obb.fixedincome.rate.ecb(provider='fred')
obb.fixedincome.rate.ecb(interest_rate_type='refinancing', provider='fred')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| interest_rate_type | Literal['deposit', 'lending', 'refinancing'] | The type of interest rate. | lending | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| interest_rate_type | Literal['deposit', 'lending', 'refinancing'] | The type of interest rate. | lending | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : EuropeanCentralBankInterestRates
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
| rate | float | European Central Bank Interest Rate. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | European Central Bank Interest Rate. |
</TabItem>

</Tabs>

