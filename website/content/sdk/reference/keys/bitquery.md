---
title: bitquery
description: This documentation page is dedicated to the Bitquery key setting process
  in the OpenBB Terminal application. Learn how to set API keys, understand the use
  of environment variables, and follow practical examples using the Python language
  in a Jupyter Notebook environment.
keywords:
- Bitquery
- API Key
- Setting Key
- Environment Variables
- Jupyter Notebook
- Terminal
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.bitquery - Reference | OpenBB SDK Docs" />

Set Bitquery key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1059)]

```python
openbb.keys.bitquery(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.bitquery(key="example_key")
```

---
