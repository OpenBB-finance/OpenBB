---
title: nftcollection
description: This page provides guidance on how to use the nftcollection command to
  retrieve NFT data, including details such as owner, items number, total minted NFTs,
  and more.
keywords:
- NFT
- nftcollection
- nft data retrieval
- nft metadata
- non-fungible token
- crypto
- cryptopunks
- chart
- floor price
- sales
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="nft: nftcollection - Telegram Reference | OpenBB Bot Docs" />

This command retrieves a collection of Non-Fungible Token (NFT) data associated with the specified slug. It returns the collection's metadata, including the owner, the number of items in the collection, the total NFTs minted, and various other data on the NFT.

### Usage

```python wordwrap
/nftcollection slug [chart]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| slug | NFT collection slug (e.g., cryptopunks) | False | None |
| chart | Show chart with Floor Price and Sales (True/False) (default: False) | True | None |


---

## Examples

```
/nftcollection bent
```

```
/nftcollection bent chart
```

```
/nftcollection bent y
```

---
