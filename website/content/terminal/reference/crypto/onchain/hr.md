---
title: hr
description: Documentation on the 'hr' function to view the mean hashrate of BTC or
  ETH over a specific frequency interval. Contains information on command usage and
  the parameters involved.
keywords:
- blockchain
- hashrate
- BTC
- ETH
- coin
- cryptocurrency
- frequency interval
- Glassnode
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/onchain/hr - Reference | OpenBB Terminal Docs" />

Display mean hashrate for a certain blockchain (ETH or BTC) [Source: https://glassnode.org]

### Usage

```python
hr [-c {BTC,ETH}] [-i {24h,1w,1month}] [-s SINCE] [-u UNTIL]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| coin | Coin to check hashrate (BTC or ETH) | BTC | True | BTC, ETH |
| interval | Frequency interval. Default: 24h | 24h | True | 24h, 1w, 1month |
| since | Initial date. Default: 2021-11-25 | 2021-11-25 | True | None |
| until | Final date. Default: 2022-11-25 | 2022-11-25 | True | None |

![hr](https://user-images.githubusercontent.com/46355364/154067420-9fdd9324-c4f2-4bb4-91c1-4c675e4b45d1.png)

---
