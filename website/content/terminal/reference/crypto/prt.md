---
title: prt
description: The Potential Returns Tool page provides detailed usage and parameter
  information for the tool which helps users estimate returns from various cryptocurrencies
  if they reach a certain price or market cap. The tool utilizes data from CoinGecko.
keywords:
- Potential Returns Tool
- cryptocurrency
- market cap
- coin data
- CoinGecko
- compare crypto
- crypto price
- top N coins
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /prt - Reference | OpenBB Terminal Docs" />

Potential Returns ToolTool to check returns if loaded coin reaches provided price or other crypto market capUses CoinGecko to grab coin data (price and market cap).

### Usage

```python
prt [--vs VS] [-p PRICE] [-t TOP]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| vs | Coin to compare with | None | True | None |
| price | Desired price | None | True | None |
| top | Compare with top N coins | None | True | None |

---
