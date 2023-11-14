---
title: list
description: This page contains information on how to list the order history using
  specific parameters such as order state and limit retrieval. It provides guidance
  on the usage and parameters to maximize functionality.
keywords:
- list order history
- Usage
- parameters
- state order
- limit order retrieval
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex/oanda/list - Reference | OpenBB Terminal Docs" />

List order history

### Usage

```python
list [-s STATE] [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| state | List orders that have a specific state. | ALL | True | None |
| limit | Limit the number of orders to retrieve. | 20 | True | None |

---
