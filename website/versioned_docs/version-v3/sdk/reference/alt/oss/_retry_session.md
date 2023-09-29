---
title: _retry_session
description: OpenBB SDK Function
---

# _retry_session

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

