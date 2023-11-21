---
title: reddit
description: The documentation page provides information on how to set Reddit API
  keys using openbb_terminal's Python SDK. It lays out detailed procedures to establish
  Reddit's client id and client secret for authentication. The page also explains
  defaults and optional parameters including user credentials and options for API
  key persistence.
keywords:
- Reddit API
- openbb keys
- Reddit client id
- Reddit client secret
- Reddit authentication
- openbb_terminal
- Python SDK
- API setting
- API key
- User credentials
- Jupyter notebook
- Environment variables
- Status string
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="keys.reddit - Reference | OpenBB SDK Docs" />

Set Reddit key

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/keys_model.py#L942)]

```python
openbb.keys.reddit(client_id: str, client_secret: str, password: str, username: str, useragent: str, persist: bool = False, show_output: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| client_id | str | Client ID | None | False |
| client_secret | str | Client secret | None | False |
| password | str | User password | None | False |
| username | str | User username | None | False |
| useragent | str | User useragent | None | False |
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
openbb.keys.reddit(
```

```
client_id="example_id",
        client_secret="example_secret",
        password="example_password",
        username="example_username",
        useragent="example_useragent"
    )
```
---
