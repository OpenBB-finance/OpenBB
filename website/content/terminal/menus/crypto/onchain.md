---
title: Onchain
description: This page provides insight into the Cryptocurrency Onchain menu. It discusses
  how to use the menu for leveraging blockchain ledger data and scrutinizing transaction
  data and crypto wallet balances. These features are crucial in deciding whether
  to invest in a specific cryptocurrency. The page also provides examples of how to
  view top traded crypto pairs and find information about specific Ethereum addresses.
keywords:
- Cryptocurrency
- Onchain
- Blockchain
- Investing
- Market Sentiment
- Blockchain Ledger Data
- Transaction Data
- Crypto Wallet Balances
- Top Traded Crypto Pairs
- Ethereum Address
- Historical Transactions
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Onchain - Crypto - Data Available | OpenBB Terminal Docs" />

The Onchain sub-menu provides insights to the activities recorded on the blockchain.  Enter the menu by typing, `onchain`, into the Terminal from Crypto menu, or with the absolute path:

```console
/crypto/onchain
```

![Screenshot 2023-10-31 at 11 17 42 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/1d9f7deb-a725-46ca-adc3-033613b63fb9)

## Usage

The menu is divided into two sections, with the bottom half dedicated to individual Ethereum addresses.

### Whales

The `whales` command shows where large blocks are being traded.

```console
/crypto/onchain/whales
```

![Screenshot 2023-10-31 at 11 30 17 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/b9c888d8-3bc9-4f0f-ad2a-96adf4e456df)

### Address

Load an Ethereum wallet address with the `address` command.

```console
address --address 0x40B38765696e3d5d8d9d834D8AaD4bB6e418E489
```

Add `-t` to the command if the address is an ERC20 token address.

Add `-tx` to the command if the address is a transaction hash.

### Balance

After an address is loaded, use `balance` to check out what it's holding.

```console
balance
```

![Screenshot 2023-10-31 at 12 33 48 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/c8ef0b1f-d681-42d5-9082-3a358e6bc624)
