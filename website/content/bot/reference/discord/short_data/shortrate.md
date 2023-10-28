---
title: shortrate
description: A comprehensive guide to using the shortrate command to check Interactive
  Brokers' Display Short Shares spot borrow rates. Helps users make informed decisions
  about short selling activities.
keywords:
- shortrate command
- Interactive Brokers
- spot borrow rates
- short selling
- Display Short Shares
- stock ticker
- shortrate usage
- shortrate examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="short_data: shortrate - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the Display Short Shares spot borrow rate from Interactive Brokers for the given ticker. The spot borrow rate is the rate at which a user may borrow shares from the broker in order to short sell the security. This command allows the user to check the current rate and make more informed decisions about their short selling activities.

### Usage

```python wordwrap
/sh shortrate ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/sh shortrate ticker:AMD
```

---
