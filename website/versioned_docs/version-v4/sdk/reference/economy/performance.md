---
title: performance
description: OpenBB SDK Function
---

# performance

Get group (sectors, industry or country) performance data. [Source: Finviz]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/finviz_model.py#L112)]

```python
openbb.economy.performance(group: str = "sector", sortby: str = "Name", ascend: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| group | str | Group by category. Available groups can be accessed through get_groups(). | sector | True |
| sortby | str | Column to sort by | Name | True |
| ascend | bool | Flag to sort in ascending order | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | dataframe with performance data |
---

