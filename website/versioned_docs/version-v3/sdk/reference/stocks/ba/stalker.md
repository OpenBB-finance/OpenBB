---
title: stalker
description: OpenBB SDK Function
---

# stalker

Gets messages from given user [Source: stocktwits].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/stocktwits_model.py#L103)]

```python
openbb.stocks.ba.stalker(user: str, limit: int = 30)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| user | str | User to get posts for | None | False |
| limit | int | Number of posts to get, by default 30 | 30 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| List[Dict[str, Any]] | List of posts |
---

