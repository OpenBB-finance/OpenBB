---
title: maxpain
description: The page provides information on the maxpain function that finds the
  maximum pain on expiration date for a particular stock. It includes usage, parameters,
  and examples.
keywords:
- Max Pain
- Stock options
- Expiration date
- Option holders
- Financial losses
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: maxpain - Discord Reference | OpenBB Bot Docs" />

This command retrieves the Max Pain on expiration date for a given stock. Max Pain is the strike price with the most open options contracts and it is the price at which the stock would cause financial losses for the largest number of option holders at expiration.

### Usage

```python wordwrap
/op maxpain ticker expiry
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
/op maxpain ticker:AMC expiry:2022-07-29
```

---
