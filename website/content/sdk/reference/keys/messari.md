---
title: messari
description: This page deals with details on setting the Messari key in the OpenBB
  finance terminal. It highlights on parameters such as API key, the persist and show_output
  options and also provides an example of how to use the openbb.keys.messari function.
keywords:
- OpenBB terminal
- Messari key
- API key
- Parameters
- openbb.keys.messari function
- example usage
- persist
- show_output
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.messari - Reference | OpenBB SDK Docs" />

Set Messari key.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L2205)]

```python
openbb.keys.messari(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.messari(key="example_key")
```

---
