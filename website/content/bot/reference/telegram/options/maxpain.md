---
title: maxpain
description: This page provides instructions on how to use the maxpain command to
  retrieve the max pain on expiration date for any given stock. It is the most efficient
  guide to using the maxpain feature for tracking a stock's strike price where maximum
  financial losses may occur for the largest number of option holders.
keywords:
- maxpain command
- max pain
- stock options
- strike price
- expiration date
- financial losses
- option holders
- stock ticker
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: maxpain - Telegram Reference | OpenBB Bot Docs" />

This command retrieves the Max Pain on expiration date for a given stock. Max Pain is the strike price with the most open options contracts and it is the price at which the stock would cause financial losses for the largest number of option holders at expiration.

### Usage

```python wordwrap
/maxpain ticker expiry
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date | False | None |


---

## Examples

```
/maxpain AMC 2022-07-29
```
---
