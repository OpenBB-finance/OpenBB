---
title: moody
description: Explore and analyze the Moody Corporate Bond Index and Moody's Aaa and
  Baa investment bonds. Find the performance, rating, and interest rate information.
  Use the ``moody()`` function in Python to retrieve the data with customizable parameters.
keywords:
- Moody Corporate Bond Index
- Moody's Aaa
- Moody's Baa
- investment bonds
- index
- performance
- Aaa rating
- Baa rating
- Moody's Investors Service
- macroeconomics
- interest rate
- python
- start date
- end date
- index type
- provider
- fred
- spread
- results
- provider name
- warnings
- chart
- metadata
- data
- rate
---



<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Moody Corporate Bond Index.

Moody's Aaa and Baa are investment bonds that acts as an index of
the performance of all bonds given an Aaa or Baa rating by Moody's Investors Service respectively.
These corporate bonds often are used in macroeconomics as an alternative to the federal ten-year
Treasury Bill as an indicator of the interest rate.

```python wordwrap
obb.fixedincome.corporate.moody(start_date: Union[date, str] = None, end_date: Union[date, str] = None, index_type: Literal[str] = aaa, provider: Literal[str] = fred)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| index_type | Literal['aaa', 'baa'] | The type of series. | aaa | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| index_type | Literal['aaa', 'baa'] | The type of series. | aaa | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| spread | Literal['treasury', 'fed_funds'] | The type of spread. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[MoodyCorporateBondIndex]
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
| rate | float | Moody Corporate Bond Index Rate. |
</TabItem>

</Tabs>
