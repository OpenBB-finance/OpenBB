---
title: global_deaths
description: This page provides understanding about the function 'global_deaths' from
  OpenBB.terminals used to fetch historical death statistics for a specified country
  due to covid.
keywords:
- OpenBB.terminals
- global_deaths
- covid
- historical death data
- python function
- dataframe
- country specific statistics
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.covid.global_deaths - Reference | OpenBB SDK Docs" />

Get historical deaths for given country.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/covid/covid_model.py#L73)]

```python
openbb.alt.covid.global_deaths(country: str)
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
| pd.DataFrame | Dataframe of historical deaths |
---
