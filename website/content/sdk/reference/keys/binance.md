---
title: binance
description: This documentation page provides information on how to set Binance keys
  using the openbb_terminal sdk, including a detailed overlook of the parameters and
  returns.
keywords:
- binance
- API key
- API secret
- openbb_terminal sdk
- Jupyter notebook session
- terminal environment variables
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.binance - Reference | OpenBB SDK Docs" />

Set Binance key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1473)]

```python
openbb.keys.binance(key: str, secret: str, persist: bool = False, show_output: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| key | str | API key | None | False |
| secret | str | API secret | None | False |
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
openbb.keys.binance(
```

```
key="example_key",
        secret="example_secret"
    )
```
---
