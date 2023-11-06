---
title: oi
description: This documentation page provides an understanding about the oi command
  which allows users to retrieve the Open Interest and Call/Put ratio for a given
  stock. One can also specify an expiration date to get a more specific breakdown.
keywords:
- Open Interest
- Call/Put ratio
- Stock Ticker
- Expiration Date
- oi command
- AMC
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: oi - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the Open Interest and Call/Put ratio for a given stock. Optionally, the user can also specify an expiration date to get a more granular breakdown.

### Usage

```python wordwrap
/oi ticker [expiry]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date | True | None |


---

## Examples

```
/oi AMC
```

```
/oi AMC 2022-07-29
```
---
