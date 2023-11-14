---
title: btccp
description: btccp displays the Bitcoin (BTC) circulating supply with ranging parameters.
  It uses data sourced from blockchain's API while offering a customizable date range.
keywords:
- Bitcoin
- BTC
- circulating supply
- blockchain API
- cryptocurrency
- data visualization
- btccp
- data extraction
- date parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/onchain/btccp - Reference | OpenBB Terminal Docs" />

Display BTC circulating supply [Source: https://api.blockchain.info/]

### Usage

```python
btccp [-s SINCE] [-u UNTIL]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| since | Initial date. Default: 2010-01-01 | 2010-01-01 | True | None |
| until | Final date. Default: 2021-01-01 | 2022-11-25 | True | None |

![btccp](https://user-images.githubusercontent.com/46355364/154067527-0916ab9d-4690-4077-9037-a2665f9fc593.png)

---
