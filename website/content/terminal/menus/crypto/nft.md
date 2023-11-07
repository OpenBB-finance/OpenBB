---
title: Non Fungible Token (NFT)
description: This page provides an introduction to the Non Fungible Token (NFT) sub-menu within the Crypto menu of the OpenBB Terminal.
keywords:
- Non Fungible Token
- NFT
- /crypto/nft
- stats
- metrics
- collections
- crypto menu
- nft menu
- mutant-ape-yacht-club
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Non Fungible Token (NFT) - Crypto - Menus | OpenBB Terminal Docs" />

The Non Fungible Token (NFT) menu is a place to lookup stats and find collections of NFT projects.

## Usage

Enter the menu by typing, `nft`, into the Terminal from the Crypto menu, or with the absolute path.

```console
/crypto/nft
```

![Screenshot 2023-10-31 at 11 01 12 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/af546da0-933f-4c5d-9436-a599e2e51743)

### Collections

`collections` shows a list of projects containing basic stats.

```console
/crypto/nft/collections
```

![Screenshot 2023-10-31 at 11 10 06 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/1f566704-08d9-4d66-9089-fca29bda045a)

### FP

The `fp` command is a time series chart displaying sales and the floor price of a specific collection.

![Screenshot 2023-10-31 at 11 11 23 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/b91803e2-14af-45be-84a4-ea5ae94557dd)

```console
/crypto/nft/fp -s adidas-golden-ticket
```

![Screenshot 2023-10-31 at 11 14 25 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/31056539-e0ac-4c1d-ad19-d6076d380f65)

