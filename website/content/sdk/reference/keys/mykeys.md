---
title: mykeys
description: This documentation page offers detailed instructions on how to get currently
  set API keys using the OpenBB finance mykeys function. Includes parameter descriptions,
  return types, and usage examples.
keywords:
- API keys
- OpenBB finance
- mykeys function
- Parameters
- Return types
- Examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.mykeys - Reference | OpenBB SDK Docs" />

Get currently set API keys.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L241)]

```python
openbb.keys.mykeys(show: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| show | bool | Flag to choose whether to show actual keys or not.<br/>By default, False. | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Currents keys |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.keys.mykeys()
```

```
Key
          API
 BITQUERY_KEY  *******
      CMC_KEY  *******
COINGLASS_KEY  *******
```
---
