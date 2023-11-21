---
title: github_data
description: This page provides the function 'openbb.alt.oss.github_data' to retrieve
  repository stats from a specified GitHub API endpoint using Python. It includes
  a list of parameters for this function and explains what data you will retrieve.
keywords:
- github data
- repository stats
- openbb.alt.oss.github_data
- github api endpoint
- params
- api endpoint
- dictionary data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.oss.github_data - Reference | OpenBB SDK Docs" />

Get repository stats.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/github_model.py#L21)]

```python
openbb.alt.oss.github_data(url: str, kwargs: Any)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| url | str | github api endpoint | None | False |
| params | dict | params to pass to api endpoint | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Dict[str, Any] | Dictionary with data |
---
