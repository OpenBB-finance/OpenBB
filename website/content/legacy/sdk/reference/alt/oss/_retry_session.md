---
title: _retry_session
description: The _retry_session function in OpenBBTerminal is a Python helper method
  that attempts to mount a session given a URL, implementing a retry scheme with parameters
  for number of retries and a backoff factor. It returns a session object from the
  requests library.
keywords:
- _retry_session
- url
- retries
- backoff_factor
- requests.Session
- session mount
- retry scheme
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.oss._retry_session - Reference | OpenBB SDK Docs" />

Helper methods that retries to make request.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/runa_model.py#L32)]

```python
openbb.alt.oss._retry_session(url: str, retries: int = 3, backoff_factor: float = 1.0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| url | str | Url to mount a session | None | False |
| retries | int | How many retries | 3 | True |
| backoff_factor | float | Backoff schema - time periods between retry | 1.0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| requests.Session | Mounted session |
---
