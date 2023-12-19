---
title: santiment
description: Detailed documentation on how to set the Santiment API key using the
  OpenBB-Terminal SDK. Instructions and examples are provided, including parameters
  for optional persistence and output display.
keywords:
- Santiment key
- API key
- OpenBB-Terminal
- SEO for Documentation
- Document SEO
- Persist Key
- Show Output
- Jupyter Notebook
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.santiment - Reference | OpenBB SDK Docs" />

Set Santiment key.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L2335)]

```python
openbb.keys.santiment(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.santiment(key="example_key")
```

---
