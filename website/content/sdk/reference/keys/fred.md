---
title: fred
description: This page provides thorough instructions for setting up a FRED key in
  the OpenBB Terminal Python environment, including guidelines for its use within
  a Jupyter notebook session or as a global terminal environment variable. Examples
  of correct usage and behaviors are also provided.
keywords:
- FRED Key
- OpenBB terminal
- API key
- Jupyter notebook session
- terminal environment variables
- Status of key set
- openbb_terminal.sdk
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.fred - Reference | OpenBB SDK Docs" />

Set FRED key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L548)]

```python
openbb.keys.fred(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.fred(key="example_key")
```

---
