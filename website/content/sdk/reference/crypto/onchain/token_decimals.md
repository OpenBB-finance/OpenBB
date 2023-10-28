---
title: token_decimals
description: The page provides a detailed guide on using helper methods to identify
  token decimal number using OpenBB Crypto's Onchain and Ethplorer model. It provides
  insightful information about token decimals and how to fetch this information using
  a given address. Ideal for users interacting with Ethereum-based tokens.
keywords:
- token decimals
- blockchain balance
- OpenBB crypto
- onchain
- ethplorer model
- crypto token decimals
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.token_decimals - Reference | OpenBB SDK Docs" />

Helper methods that gets token decimals number. [Source: Ethplorer]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethplorer_model.py#L176)]

```python
openbb.crypto.onchain.token_decimals(address: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | Blockchain balance e.g. 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984 | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Optional[int] | Number of decimals for given token. |
---
