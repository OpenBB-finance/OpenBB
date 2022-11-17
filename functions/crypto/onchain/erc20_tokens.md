---
title: erc20_tokens
description: OpenBB SDK Function
---

# erc20_tokens

## crypto_onchain_bitquery_model.get_erc20_tokens

```python title='openbb_terminal/cryptocurrency/onchain/bitquery_model.py'
def get_erc20_tokens() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L210)

Description: Helper method that loads ~1500 most traded erc20 token.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | ERC20 tokens with address, symbol and name |

## Examples

