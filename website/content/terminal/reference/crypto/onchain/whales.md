---
title: whales
description: A page that provides information on the use of the 'whales' feature to
  display significant cryptocurrency transactions. It explains parameters for customization
  like minimum value, record limit, sort order, etc.
keywords:
- Crypto whales transactions
- Cryptocurrency
- Docusaurus
- Crypto transaction tracking
- Crypto address details
- Sort crypto transactions
- Crypto trade parameters
- Display major crypto transactions
- Sort by date, amount, blockchain
- Limit number of crypto records
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/onchain/whales - Reference | OpenBB Terminal Docs" />

Display crypto whales transactions. [Source: https://docs.whale-alert.io/]

### Usage

```python
whales [-m MIN] [-l LIMIT] [-s {date,symbol,blockchain,amount,amount_usd,from,to}] [-r] [-a]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| min | Minimum value of transactions. | 1000000 | True | None |
| limit | display N number records | 10 | True | None |
| sortby | Sort by given column. Default: date | date | True | date, symbol, blockchain, amount, amount_usd, from, to |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| address | Flag to show addresses of transaction | False | True | None |

---
