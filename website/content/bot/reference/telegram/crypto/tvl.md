---
title: tvl
description: On this page, users can learn how to retrieve historical TVL (Total Value
  Locked) data for any given protocol, providing a snapshot of capital currently locked
  in the protocol for comparison and tracking of growth over time.
keywords:
- TVL
- historical data
- total value locked
- protocol
- capital
- comparison
- tracking growth
- tvl command
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto: tvl - Telegram Reference | OpenBB Bot Docs" />

This command allows users to retrieve historical TVL (Total Value Locked) data for any given protocol. It provides a snapshot of the total amount of capital that is currently locked in the protocol, allowing users to easily compare the metrics between different protocols and track their growth over time.

### Usage

```python wordwrap
/tvl [protocols]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| protocols | comma separated list of protocols (e.g., curve,makerdao) | True | None |


---

## Examples

```
/tvl
```
```
/tvl curve
```

---
