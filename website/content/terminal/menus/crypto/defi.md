---
title: Decentralized Finance (DeFi)
description: This doc provides information on the DeFi sub-menu, within the Crypto menu of the OpenBB Terminal.
keywords:
- Cryptocurrency
- Decentralized Finance
- DeFi
- tvl
- pancakeswap
- sushiswap
- dApps information
- tokens
- stats
- pairs
- gdapps
- stvl
- crypto menu
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="DeFi - Crypto - Menus | OpenBB Terminal Docs" />

The DeFi sub-menu sports a small collection of functions, with data largely coming from DeFi Llama.

## Usage

Enter the menu with:

```console
/crypto/defi
```

### ldapps

The `ldapps` command will return a list of DeFi apps.  Use the `--limit` argument to increase the number of results returned.

```console
/crypto/defi/ldapps --limit 1000
```

![Screenshot 2023-10-31 at 9 12 46 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/20e20089-080d-4172-a305-2d9ce364e1e9)


### stvl

`stvl` is a time series representing the total value locked across the DeFi space.  Use the `--limit` argument here for the number of days to look back.

```console
/crypto/defi/stvl --limit 1000
```

![Screenshot 2023-10-31 at 9 49 36 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/41e67090-1db5-4ea9-946d-71887672b85a)
