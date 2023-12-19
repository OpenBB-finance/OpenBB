---
title: tokenterminal
description: This documentation page deals with the 'tokenterminal' function of the
  OpenBB finance terminal. It allows users to set a Token Terminal key, which, depending
  on the parameters, can be limited to the current session or applied globally. A
  use-case example is also included.
keywords:
- Token Terminal Key
- API Key
- Finance Terminal
- tokenterminal Function
- Terminal Environment Variables
- Jupyter Notebook
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.tokenterminal - Reference | OpenBB SDK Docs" />

Set Token Terminal key.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L2483)]

```python
openbb.keys.tokenterminal(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.tokenterminal(key="example_key")
```

---
