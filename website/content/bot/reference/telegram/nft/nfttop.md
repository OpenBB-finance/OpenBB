---
title: nfttop
description: The page provides comprehensive details on the 'nfttop' command, which
  fetches the top NFT collections from Ethereum. It includes parameter details and
  command usage examples.
keywords:
- nfttop command
- NFT collections
- Ethereum
- popular NFTs
- nfttop parameters
- command usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="nft: nfttop - Telegram Reference | OpenBB Bot Docs" />

This command allows users to retrieve the top NFT collections from Ethereum. It provides a list of the most popular and valuable NFT collections, helping users to keep abreast of the latest trends in the NFT space.

### Usage

```python wordwrap
/nfttop [sortby] [interval] [reverse]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| sortby | Sort by (default: mc) | True | mc, floor, vol, sales |
| interval | Interval (default: 1d) | True | 1d, 7d, 30d, 90d |
| reverse | Default: `false` | True | None |


---

## Examples

```
/nfttop
```

```
/nfttop mc y
```

---
