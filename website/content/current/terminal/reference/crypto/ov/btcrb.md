---
title: btcrb
description: btcrb is a Python-based tool offering visualization of Bitcoin Rainbow
  chart over time which includes halvings. Its primary data source is Glassnode and
  it's inspired by Blockchaincenter.net.
keywords:
- btcrb
- bitcoin
- rainbow chart
- glassnode
- blockchaincenter.net
- BTC
- cryptocurrency
- halvings
- price data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/ov/btcrb - Reference | OpenBB Terminal Docs" />

Display bitcoin rainbow chart overtime including halvings. [Price data from source: https://glassnode.com] [Inspired by: https://blockchaincenter.net]

### Usage

```python
btcrb [-s SINCE] [-u UNTIL]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| since | Initial date. Default is initial BTC date: 2010-01-01 | 2010-01-01 | True | None |
| until | Final date. Default is current date | 2022-11-25 | True | None |

![btcrb](https://user-images.githubusercontent.com/46355364/154068553-f40e8a63-dd69-4508-a0f1-d91cfd5e6e9b.png)

---
