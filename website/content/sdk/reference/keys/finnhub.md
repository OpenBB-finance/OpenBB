---
title: finnhub
description: This page provides information on setting up the Finnhub API key in the
  OpenBB terminal environment, with code implementation examples.
keywords:
- Finnhub
- API key
- OpenBB terminal
- Python SDK
- Jupyter notebook
- Environment variables
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.finnhub - Reference | OpenBB SDK Docs" />

Set Finnhub key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L813)]

```python
openbb.keys.finnhub(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.finnhub(key="example_key")
```

---
