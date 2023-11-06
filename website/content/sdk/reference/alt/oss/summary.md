---
title: summary
description: This documentation page contains comprehensive information on OpenBB's
  repository summary and chart view options. You can retrieve a summary with OpenBB
  library and display it in a chart view. Includes source code links and detailed
  parameter descriptions for usage.
keywords:
- Repository Summary
- Chart View
- Source Code
- Github
- Docusaurus
- API
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.oss.summary - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get repository summary.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/github_model.py#L179)]

```python
openbb.alt.oss.summary(repo: str)
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
| pd.DataFrame | Dataframe with repo summary - Columns: Metric, Value |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing repo summary [Source: https://api.github.com].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/github_view.py#L123)]

```python
openbb.alt.oss.summary_chart(repo: str, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| repo | str | Repository to display summary. Format: org/repo, e.g., openbb-finance/openbbterminal | None | False |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
