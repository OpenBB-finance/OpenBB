---
title: nft_mktp
description: Shows NFT marketplaces [Source https//dappradar
keywords:
- crypto.disc
- nft_mktp
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /disc/nft_mktp - Reference | OpenBB Terminal Docs" />

Shows NFT marketplaces [Source: https://dappradar.com/] Accepts --chain to filter by blockchain --sortby {name, avgPrice, volume, traders...} to sort by column --order {asc, desc} to sort ascending or descending --limit to limit number of records

### Usage

```python wordwrap
nft_mktp [-c CHAIN] [-s SORTBY [SORTBY ...]] [-o ORDER] [-l LIMIT]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| chain | -c  --chain | Name of the blockchain to filter by. | None | True | None |
| sortby | -s  --sortby | Sort by given column. | None | True | name, dapp_id, logo, chains, avg_price_[$], avg_price_change_[%], volume_[$], volume_change_[%], traders, traders_change_[%] |
| order | -o  --order | Order of sorting. Default: desc | desc | True | None |
| limit | -l  --limit | Number of records to display | 10 | True | None |

---
