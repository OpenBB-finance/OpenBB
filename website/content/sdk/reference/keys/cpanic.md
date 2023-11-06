---
title: cpanic
description: This page contains detailed information regarding the cpanic function
  of OpenBB Terminal. It explains how to set the Cpanic key including parameters,
  results, and examples.
keywords:
- Python SDK
- API key management
- cpanic function
- environment variables
- Jupyter notebook
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.cpanic - Reference | OpenBB SDK Docs" />

Set Cpanic key.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1924)]

```python
openbb.keys.cpanic(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.cpanic(key="example_key")
```

---
