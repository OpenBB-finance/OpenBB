---
title: oi
description: The documentation details about 'oi' command allows the user to retrieve
  the Open Interest and Call/Put ratio for a specific stock. Additional functionality
  includes setting an expiration date for a more granular breakdown.
keywords:
- oi command
- Open Interest
- Call/Put ratio
- stock
- expiry
- granular breakdown
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: oi - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the Open Interest and Call/Put ratio for a given stock. Optionally, the user can also specify an expiration date to get a more granular breakdown.

### Usage

```python wordwrap
/op oi ticker [expiry]
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
/op oi ticker:AMC
```

```
/op oi ticker:AMC expiry:2022-07-29
```

---
