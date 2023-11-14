---
title: sumexp
description: A documentation descriptor for the command 'sumexp', a function which
  allows users to obtain total premium of a specified stock ticker in the current
  trading day by expiration. Users can distinguish calls and puts depending on where
  the trade happened on the bid/ask.
keywords:
- sumexp
- trading
- stock ticker
- option trading
- trade on bid/ask
- premium retrieval
- expiration date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flow: sumexp - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the total premium of the given stock ticker for the current trading day by expiration. We categorize the calls and puts by where the trade occurred on the bid/ask. For example, Above Ask, means the trade happened over the current Ask price.

### Usage

```python wordwrap
/flow sumexp ticker expiry
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
/flow sumexp ticker:AMD expiry:2022-07-29
```

---
