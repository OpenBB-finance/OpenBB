---
title: sectors
description: 'The page contains information about the ''sectors'' command that retrieves
  a summary of all prints by % of MarketCap by Sector over the last x days. The details
  include the command usage, parameters required and examples to follow. '
keywords:
- sectors command
- MarketCap by sector
- darkpool activity
- sector market cap
- accumulation
- days parameter
- sector parameter
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="darkpool: sectors - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a summary of all prints by % of MarketCap by Sector over the last x days. The user will be able to view the sector's market cap divided by total darkpool activity to see possible accumulation.

### Usage

```python wordwrap
/sectors days sector
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| days | Number of days to look back | False | None |
| sector | Sector to filter by: `bm`: (Basic Materials), `e`: (Energy), `cs`: (Communication Services), `cc`: (Consumer Cyclical), `cd`: (Consumer Defensive), `f`: (Financial), `h`: (Healthcare), `i`: (Industrials), `re`: (Real Estate), `t`: (Technology), `u`: (Utilities) | False | None |


---

## Examples

```
/sectors 5 bm
```

---
