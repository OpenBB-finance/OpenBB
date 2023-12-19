---
title: news
description: This page provides information about the 'Set News key' feature in the
  OpenBB Terminal. Learn how to use the function, understand the parameters and returns,
  and see use-cases in Python code examples.
keywords:
- OpenBB Terminal documentation
- Set News key function
- API keys
- Python code examples
- OpenBB SDK
- terminal environment variables
- Change API key
- Jupyter notebook sessions
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.news - Reference | OpenBB SDK Docs" />

Set News key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L614)]

```python
openbb.keys.news(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.news(key="example_key")
```

---
