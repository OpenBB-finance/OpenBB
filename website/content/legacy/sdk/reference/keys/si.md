---
title: si
description: This page provides a guide on how to set the Sentimentinvestor key using
  OpenBB terminal. It explains the parameters and returns of the function, including
  examples demonstrating its use.
keywords:
- Sentimentinvestor
- API key
- OpenBB terminal
- terminal environment variables
- Jupyter notebook
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.si - Reference | OpenBB SDK Docs" />

Set Sentimentinvestor key.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1548)]

```python
openbb.keys.si(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.si(key="example_key")
```

---
