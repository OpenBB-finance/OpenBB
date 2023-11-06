---
title: collection
description: This documentation page details the procedure to retrieve a collection
  of Non-Fungible Token (NFT) data, including metadata such as the owner and the number
  of items in the collection.
keywords:
- NFT
- Non-Fungible Token
- cryptocurrency
- collection
- metadata
- ownership
- minted NFTs
- slug
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="nft: collection - Discord Reference | OpenBB Bot Docs" />

This command retrieves a collection of Non-Fungible Token (NFT) data associated with the specified slug. It returns the collection's metadata, including the owner, the number of items in the collection, the total NFTs minted, and various other data on the NFT.

### Usage

```python wordwrap
/nft collection slug
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| slug | NFT collection slug (e.g., cryptopunks) | False | None |


---

## Examples

```
/nft collection slug: bent
```

---
