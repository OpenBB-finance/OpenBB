---
title: address
description: This page provides a guide to loading and analyzing account addresses,
  token addresses and transaction hashes on Ethplorer with Python. Learn how to use
  parameters for efficient analysis.
keywords:
- ethplorer
- address
- account address
- token address
- transaction hash
- erc20
- ethereum
- analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/onchain/address - Reference | OpenBB Terminal Docs" />

Load address for further analysis. You can analyze account address, token address or transaction hash. [Source: Ethplorer]

### Usage

```python
address [-a] [-t] [-tx] --address ADDRESS
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| account | Account address | False | True | None |
| token | ERC20 token address | False | True | None |
| transaction | Transaction hash | False | True | None |
| address | Ethereum address | False | False | None |

---
