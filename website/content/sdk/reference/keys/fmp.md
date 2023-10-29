---
title: fmp
description: This page provides a guide for setting the Financial Modeling Prep API
  key using the OpenBB Terminal. It covers parameters to set the key, adjusting the
  persist and show_output options, and an example of usage.
keywords:
- Financial Modeling Prep
- API key
- set api key
- openbb.keys.fmp
- persist
- show_output
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.fmp - Reference | OpenBB SDK Docs" />

Set Financial Modeling Prep key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L352)]

```python
openbb.keys.fmp(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.fmp(key="example_key")
```

---
