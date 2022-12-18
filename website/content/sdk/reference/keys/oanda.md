---
title: oanda
description: OpenBB SDK Function
---

# oanda

Set Oanda key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1387)]

```python
openbb.keys.oanda(account: str, access_token: str, account_type: str = "", persist: bool = False, show_output: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| account | str | User account | None | False |
| access_token | str | User token | None | False |
| account_type | str | User account type |  | True |
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
openbb.keys.oanda(
```

```
account="example_account",
        access_token="example_access_token",
        account_type="example_account_type"
    )
```
---

