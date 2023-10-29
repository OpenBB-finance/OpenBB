---
title: global_cases
description: The 'global_cases' page provides code and instructions for getting historical
  Covid-19 case data for any country. Utilize the provided Python function to retrieve
  a DataFrame of historical data.
keywords:
- Covid-19
- historical data
- openbb.alt.covid.global_cases
- global cases
- country specific data
- programming
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.covid.global_cases - Reference | OpenBB SDK Docs" />

Get historical cases for given country.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/covid/covid_model.py#L26)]

```python
openbb.alt.covid.global_cases(country: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Country to search for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of historical cases |
---

## Examples

```python
df = get_global_cases("United States")
```

```
Dataframe of historical cases for United States
```
```python
df = get_global_cases("Portugal")
```

```
Dataframe of historical cases for Portugal
```
```python
df = get_global_cases("Spain")
```

```
Dataframe of historical cases for Spain
```
---
