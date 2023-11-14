---
title: chart
description: This documentation page provides user guidance on retrieving NFT collection
  data using a slug-based chart command, showcasing floor price and sales count over
  time.
keywords:
- NFT collection data
- chart command
- floor price
- sales count
- slug-based command
- cryptopunks
- bored-ape-yacht-club
- NFT chart
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="nft: chart - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the NFT Collection Data related to the specified slug. The chart will show the floor price over time and sales count.

### Usage

```python wordwrap
/nft chart slug
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| slug | NFT collection slug (e.g., cryptopunks) | False | None |


---

## Examples

```
/nft chart slug: bent
```

```
/nft chart slug: bored-ape-yacht-club
```

---
