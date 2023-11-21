---
title: hold
description: An overview of public companies holding Bitcoin or Ethereum, presenting
  key metrics like total holdings and value.
keywords:
- Bitcoin
- Ethereum
- public companies
- crypto holdings
- cryptocurrency
- digital assets
- bar chart
- Bitcoin dominance
- crypto metrics
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/ov/hold - Reference | OpenBB Terminal Docs" />

Shows overview of public companies that holds ethereum or bitcoin. You can find there most important metrics like: Total Bitcoin Holdings, Total Value (USD), Public Companies Bitcoin Dominance, Companies

### Usage

```python
hold [-c {ethereum,bitcoin}] [-l LIMIT] [--bar]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| coin | companies with ethereum or bitcoin | bitcoin | True | ethereum, bitcoin |
| limit | display N number of records | 5 | True | None |
| bar | Flag to show bar chart | False | True | None |

---
