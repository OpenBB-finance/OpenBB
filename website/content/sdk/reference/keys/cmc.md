---
title: cmc
description: This page provides the process of setting the Coinmarketcap key, it explains
  the parameters involved and gives an example of how it can be done. The topic is
  important for users who want to integrate their projects with Coinmarketcap's API.
keywords:
- Coinmarketcap
- API
- key setting
- Jupyter notebook
- openbb_terminal
- environment variables
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.cmc - Reference | OpenBB SDK Docs" />

Set Coinmarketcap key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L751)]

```python
openbb.keys.cmc(key: str, persist: bool = False, show_output: bool = False)
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
openbb.keys.cmc(key="example_key")
```

---
