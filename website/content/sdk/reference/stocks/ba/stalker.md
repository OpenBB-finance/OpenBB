---
title: stalker
description: This documentation page provides information on how to use the 'stalker'
  function from the OpenBB platform, which gathers messages from a specified user
  on Stocktwits. The source code is also available for referencing.
keywords:
- Stalker
- Messages
- User
- Posts
- Stocktwits
- Source code
- Post limit
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.stalker - Reference | OpenBB SDK Docs" />

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
