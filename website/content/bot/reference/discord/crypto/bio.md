---
title: bio
description: The Crypto Bio command retrieves key information about a specific cryptocurrency,
  such as its current price, trading volume, and market cap. Excellent for getting
  a quick snapshot of any given cryptocurrency's performance.
keywords:
- crypto
- crypto bio
- symbol
- btc
- cryptocurrency information
- market cap
- trading volume
- crypto price
- crypto metrics
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto: bio - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve fundamental information about a crypto, such as its current price, 24-hour trading volume, market cap, and other key metrics, by entering a specific crypto symbol (e.g. "BTC") as an argument.

### Usage

```python wordwrap
/crypto bio symbol
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| symbol | Crypto symbol to check information (e.g., BTC) | False | None |


---

## Examples

```
/crypto bio symbol: btc
```

---
