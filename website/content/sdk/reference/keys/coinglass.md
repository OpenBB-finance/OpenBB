---
title: coinglass
description: The page provides instructions on how to set the Coinglass key using
  the openbb module of the OpenBBTerminal. It gives details on the parameters used
  and their functionality, return types, and examples.
keywords:
- Coinglass key
- openbb module
- API key
- Jupyter notebook session
- terminal environment variables
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.coinglass - Reference | OpenBB SDK Docs" />

Set Coinglass key.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1853)]

```python
openbb.keys.coinglass(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.coinglass(key="example_key")
```

---
