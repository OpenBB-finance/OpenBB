---
title: eodhd
description: This is a documentation page for the 'set Eodhd key' functionality of
  the OpenBB software. It provides the Python code, parameters and their descriptions,
  return values, and an example on how to use the function.
keywords:
- eodhd
- api key
- parameters
- returns
- examples
- jupyter
- terminal environment variables
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.eodhd - Reference | OpenBB SDK Docs" />

Set Eodhd key.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L2273)]

```python
openbb.keys.eodhd(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.eodhd(key="example_key")
```

---
