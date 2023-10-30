---
title: coinbase
description: This page provides a detailed guide on setting up a Coinbase key using
  the OpenBBTerminal. Learn how to input your API key, secret, and passphrase. Understand
  the functionality of persist and show_output parameters in the context of your Jupyter
  notebook session and terminal environment variables.
keywords:
- coinbase
- coinbase key setup
- API key set
- openbb_terminal
- terminal environment variables
- coinbase API
- API secret
- coinbase passphrase
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.coinbase - Reference | OpenBB SDK Docs" />

Set Coinbase key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L1622)]

```python
openbb.keys.coinbase(key: str, secret: str, passphrase: str, persist: bool = False, show_output: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| key | str | API key | None | False |
| secret | str | API secret | None | False |
| passphrase | str | Account passphrase | None | False |
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
openbb.keys.coinbase(
```

```
key="example_key",
        secret="example_secret",
        passphrase="example_passphrase"
    )
```
---
