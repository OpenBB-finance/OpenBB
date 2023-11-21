---
title: login
description: Login and load user info
keywords:
- login
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title=".login - Reference | OpenBB SDK Docs" />

Login and load user info.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/core/session/sdk_session.py#L43)]

```python wordwrap
openbb.root.login(email: str = "", password: str = "", token: str = "", keep_session: bool = False, silent: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| email | str | The email. |  | True |
| password | str | The password. |  | True |
| token | str | The OpenBB Personal Access Token. |  | True |
| keep_session | bool | Keep the session, i.e., next time the user logs in,<br/>there is no need to enter the email and password or the token. | False | True |
| silent | bool | If True, the console print will be silent. | False | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.login(email="your_email", password="your_password")
```

---

