---
title: ethplorer
description: This page provides documentation on how to set the Ethplorer key in the
  OpenBB finance terminal. It includes explanations of the parameters and gives examples
  of how to use this function.
keywords:
- Ethplorer
- API key
- Documentation
- Finance
- Example
- Source Code
- Parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.ethplorer - Reference | OpenBB SDK Docs" />

Set Ethplorer key.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1987)]

```python
openbb.keys.ethplorer(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.ethplorer(key="example_key")
```

---
