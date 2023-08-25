---
title: history
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# history

<Tabs>
<TabItem value="model" label="Model" default>

Get repository star history.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/github_model.py#L88)]

```python
openbb.alt.oss.history(repo: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| repo | str | Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with star history - Columns: Date, Stars |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots repo summary [Source: https://api.github.com].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/github_view.py#L28)]

```python
openbb.alt.oss.history_chart(repo: str, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| repo | str | Repository to display star history. Format: org/repo, e.g., openbb-finance/openbbterminal | None | False |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>