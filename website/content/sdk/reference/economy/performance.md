---
title: performance
description: This page provides detailed information on retrieving group performance
  data using OpenBB's economy module. It provides explanations on parameters and return
  types along with a link to the source code.
keywords:
- OpenBB economy module
- group performance data
- Finviz
- Performance data retrieval
- Source code
- Programming
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.performance - Reference | OpenBB SDK Docs" />

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
