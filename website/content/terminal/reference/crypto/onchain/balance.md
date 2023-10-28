---
title: balance
description: Metadata for the page discussing about the 'balance' function to display
  information about tokens on given Ethereum blockchain balance. The page outlines
  how to use this function, its parameters, and their possible values.
keywords:
- ethplorer
- ethereum
- balance
- tokens
- python script
- blockchain balance
- sortby function
- ascending order
- descending order
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/onchain/balance - Reference | OpenBB Terminal Docs" />

Display info about tokens on given ethereum blockchain balance. [Source: Ethplorer]

### Usage

```python
balance [-l LIMIT] [-s {index,balance,tokenName,tokenSymbol}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 10 | True | None |
| sortby | Sort by given column. Default: index | index | True | index, balance, tokenName, tokenSymbol |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
