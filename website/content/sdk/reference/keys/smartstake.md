---
title: smartstake
description: The page provides detailed documentation on 'smartstake' function of
  the OpenBB Python SDK. This function is used to set the SmartStake API key for the
  current session or globally in terminal environment. Includes examples of usage
  and link to source code.
keywords:
- SmartStake API key
- API key setting
- Python function
- docusaurus documentation
- programming
- environment variables
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.smartstake - Reference | OpenBB SDK Docs" />

Set Smartstake key.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L2057)]

```python
openbb.keys.smartstake(key: str, access_token: str, persist: bool = False, show_output: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| key | str | API key | None | False |
| access_token | str | API token | None | False |
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
openbb.keys.smartstake(
```

```
key="example_key",
        access_token="example_access_token",
        )
```
---
