---
title: nft
description: Page covers usage and parameters of an NFT command for Dappradar. Allows
  sorting NFTs by name, protocols, floor price, average price, market cap, and volume.
keywords:
- NFT
- Dappradar
- Sort
- Market Cap
- Volume
- Floor Price
- Avg Price
- Protocols
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/disc/nft - Reference | OpenBB Terminal Docs" />

Shows top NFT collections [Source: https://dappradar.com/] Accepts --sort {Name,Protocols,Floor Price [$],Avg Price [$],Market Cap,Volume [$]} to sort by column

### Usage

```python
nft [-l LIMIT] [-s SORTBY [SORTBY ...]]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Number of records to display | 15 | True | None |
| sortby | Sort by given column. Default: Market Cap | Market Cap | True | Name, Protocols, Floor Price [$], Avg Price [$], Market Cap [$], Volume [$] |

---
