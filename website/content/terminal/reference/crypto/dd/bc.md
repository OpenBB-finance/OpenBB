---
title: bc
description: Documentation for the 'bc' command in a blockchain context - provides
  URLs for loaded coins on various blockchain explorer sites like etherscan.io or
  polkascan.io for analysing blockchain data.
keywords:
- blockchain
- blockchain explorers
- blockchain URLs
- etherescan.io
- polkascan.io
- blockchain data
- crypto
- btc.com
- tokenview.com
- blockchair.com
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/dd/bc - Reference | OpenBB Terminal Docs" />

Blockchain explorers URLs for loaded coin. Those are sites like etherescan.io or polkascan.io in which you can see all blockchain data e.g. all txs, all tokens, all contracts...

### Usage

```python
bc
```

---

## Parameters

This command has no parameters



---

## Examples

```python
2022 Feb 15, 07:10 (🦋) /crypto/dd/ $ bc
              Blockchain URLs
┌────────┬─────────────────────────────────┐
│ Metric │ Value                           │
├────────┼─────────────────────────────────┤
│ 0      │ https://blockchair.com/bitcoin/ │
├────────┼─────────────────────────────────┤
│ 1      │ https://btc.com/                │
├────────┼─────────────────────────────────┤
│ 2      │ https://btc.tokenview.com/      │
└────────┴─────────────────────────────────┘
```
---
