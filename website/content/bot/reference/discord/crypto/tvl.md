---
title: tvl
description: This page provides instructions on how to use the 'TVL' command to retrieve
  historical Total Value Locked (TVL) data for a given protocol. This data provides
  a snapshot of the total amount of capital locked in a protocol, enabling comparison
  of metrics between protocols and tracking their growth over time.
keywords:
- TVL
- Total Value Locked
- protocol
- crypto
- historical data
- growth tracking
- metrics comparison
- capital
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto: tvl - Discord Reference | OpenBB Bot Docs" />

This command allows users to retrieve historical TVL (Total Value Locked) data for any given protocol. It provides a snapshot of the total amount of capital that is currently locked in the protocol, allowing users to easily compare the metrics between different protocols and track their growth over time.

### Usage

```python wordwrap
/crypto tvl protocols
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| protocols | comma separated list of protocols (e.g., curve,makerdao) | False | None |


---

## Examples

```
/crypto tvl
```

```
/crypto tvl protocols: curve
```

---
