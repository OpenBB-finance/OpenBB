---
title: top
description: A documentation page that provides users with instructions on how to
  retrieve the top NFT collections from Ethereum using various parameters for sorting
  and intervals. Great resource for staying updated with the latest trends in the
  NFT market.
keywords:
- NFT Collections
- Ethereum
- Crypto Commands
- NFT Trends
- Top NFT Collections
- Market Cap
- Floor Price
- Sales Volume
- Reverse Sort
- Time Interval
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="nft: top - Discord Reference | OpenBB Bot Docs" />

This command allows users to retrieve the top NFT collections from Ethereum. It provides a list of the most popular and valuable NFT collections, helping users to keep abreast of the latest trends in the NFT space.

### Usage

```python wordwrap
/nft top [sortby] [interval] [reverse]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| sortby | Column to sort by (default: Market Cap) | True | Market Cap (MCap), Floor Price Change (Floor Price) |
| interval | Time interval to display Sales/Volume/Floor Price  (default: 1d) | True | 1d, 7d, 30d, 90d |
| reverse | Reverse the sort order (default: No) | True | Yes |


---

## Examples

```
/nft top
```

```
/nft top sortby: Market Cap reverse: Yes
```

---
