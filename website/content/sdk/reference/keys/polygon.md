---
title: polygon
description: This documentation is about the 'polygon' function in the OpenBB Terminal
  Python SDK. It details how the function accepts a polygon API key, and settings
  to persist or show output.
keywords:
- OpenBB Terminal SDK
- Polygon API key
- openbb.keys.polygon function
- Python SDK
- API key management
- Environment variables
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.polygon - Reference | OpenBB SDK Docs" />

Set Polygon key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L481)]

```python
openbb.keys.polygon(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.polygon(key="example_key")
```

---
