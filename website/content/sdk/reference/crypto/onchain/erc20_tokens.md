---
title: erc20_tokens
description: This page provides a helper method that loads the most traded erc20 tokens.
  It contains source code, parameters and returns for the OpenBBTerminal project's
  cryptocurrency bitquery model.
keywords:
- erc20 tokens
- most traded erc20 token
- cryptocurrency
- bitquery model
- OpenBBFinance
- token address
- token symbol
- token name
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto.onchain.erc20_tokens - Reference | OpenBB SDK Docs" />

Helper method that loads ~1500 most traded erc20 token.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L210)]

```python
openbb.crypto.onchain.erc20_tokens()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | ERC20 tokens with address, symbol and name |
---
