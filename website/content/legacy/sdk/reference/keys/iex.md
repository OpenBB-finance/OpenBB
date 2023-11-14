---
title: iex
description: This documentation provides information about the 'iex' function for
  setting the IEX Cloud key using the OpenBB terminal. The function helps users to
  set their API key with optional parameters such as persist and show_output for additional
  functionality. Use this function to easily integrate your application with the IEX
  Cloud services.
keywords:
- iex
- OpenBB terminal
- API key
- IEX Cloud
- api key setting
- openbb.keys.iex
- code documentation
- coding
- programming
- software development
- persist
- show_output
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.iex - Reference | OpenBB SDK Docs" />

Set IEX Cloud key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L879)]

```python
openbb.keys.iex(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.iex(key="example_key")
```

---
