---
title: walert
description: This documentation page describes how to set the Walert key in OpenBB
  finance's Terminal. It details the parameters, return types and provides examples
  for setting the API key.
keywords:
- API key set
- Walert key
- Python code
- Source code
- terminal environment variables
- Jupyter notebook session
- financial software
- web development
- SEO optimization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.walert - Reference | OpenBB SDK Docs" />

Set Walert key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1711)]

```python
openbb.keys.walert(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.walert(key="example_key")
```

---
