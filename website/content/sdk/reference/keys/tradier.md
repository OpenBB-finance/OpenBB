---
title: tradier
description: Learn how to set a Tradier API key in the OpenBB terminal using the 'openbb.keys.tradier'
  Python function. This documentation provides parameter info, function usage, and
  examples.
keywords:
- tradier
- api key
- openbb terminal
- sdk
- openbb keys tradier
- terminal environment variables
- function usage
- examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.tradier - Reference | OpenBB SDK Docs" />

Set Tradier key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L680)]

```python
openbb.keys.tradier(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.tradier(key="example_key")
```

---
