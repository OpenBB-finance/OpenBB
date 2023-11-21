---
title: btcct
description: The btcct page provides details on how to monitor Bitcoin confirmed transactions
  using the Blockchain API with adjustable date parameters.
keywords:
- btcct
- Bitcoin transactions
- Blockchain API
- Confirmed transactions
- BTC
- Cryptocurrency
- Crypto transactions monitoring
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /onchain/btcct - Reference | OpenBB Terminal Docs" />

Display BTC confirmed transactions [Source: https://api.blockchain.info/]

### Usage

```python wordwrap
btcct [-s SINCE] [-u UNTIL]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| since | -s  --since | Initial date. Default: 2010-01-01 | 2010-01-01 | True | None |
| until | -u  --until | Final date. Default: 2023-11-21 | 2023-11-21 | True | None |

![btcct](https://user-images.githubusercontent.com/46355364/154067586-d80059e8-cf7b-475a-990b-cf2aec7bc646.png)

---
