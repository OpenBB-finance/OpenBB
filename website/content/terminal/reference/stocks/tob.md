---
title: tob
description: This page provides insights on how to use the 'tob' function to get the
  top of a book for a loaded ticker from a selected exchange, explaining its parameters
  and usage.
keywords:
- tob function
- top of book
- loaded ticker
- selected exchange
- function usage
- parameters
- BZX
- EDGX
- BYX
- EDGA
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /tob - Reference | OpenBB Terminal Docs" />

Get top of book for loaded ticker from selected exchange

### Usage

```python
quote -t S_TICKER [-e {BZX,EDGX,BYX,EDGA}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| s_ticker | Ticker to get data for | None | False | None |
| exchange |  | BZX | True | BZX, EDGX, BYX, EDGA |

---
