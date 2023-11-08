---
title: quandl
description: This documentation page describes how to set the Quandl Key in OpenBB
  finance using Python. It provides parameters, return types, and code examples.
keywords:
- Quandl Key
- OpenBB finance
- API key
- Jupyter notebook
- terminal environment variables
- parameters
- return types
- code examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.quandl - Reference | OpenBB SDK Docs" />

Set Quandl key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L419)]

```python
openbb.keys.quandl(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.quandl(key="example_key")
```

---
