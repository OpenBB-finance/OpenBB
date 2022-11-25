---
title: global_cases
description: OpenBB SDK Function
---

# global_cases

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

