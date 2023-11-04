---
title: shortrate
description: Informative guide on how to use the shortrate command that retrieves
  Display Short Shares spot borrow rate from Interactive Brokers for a specific ticker.
  With this command, users can make more informed decisions in short selling processes.
keywords:
- stock
- short sell
- shortrate command
- borrow rate
- interactive brokers
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="short_data: shortrate - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the Display Short Shares spot borrow rate from Interactive Brokers for the given ticker. The spot borrow rate is the rate at which a user may borrow shares from the broker in order to short sell the security. This command allows the user to check the current rate and make more informed decisions about their short selling activities.

### Usage

```python wordwrap
/shortrate ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/shortrate AMD
```
---
