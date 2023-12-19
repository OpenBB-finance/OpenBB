---
title: github
description: The page guides users on how to set a GitHub API key using the OpenBBTerminal.
  It provides explanations about the parameters involved and gives a brief glimpse
  into the possible return values. The page also includes code examples as useful
  guidance.
keywords:
- github
- API key
- key set
- terminal environment variables
- Jupyter notebook session
- key persistence
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.github - Reference | OpenBB SDK Docs" />

Set GitHub key.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L2148)]

```python
openbb.keys.github(key: str, persist: bool = False, show_output: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| key | str | API key | None | False |
| persist | bool | If False, api key change will be contained to where it was changed. For example, a Jupyter notebook session.<br/>If True, api key change will be global, i.e. it will affect terminal environment variables.<br/>By default, False. | False | True |
| show_output | bool | Display status string or not. By default, False. | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| str | Status of key set |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.keys.github(key="example_key")
```

---
