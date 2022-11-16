---
title: token_decimals
description: OpenBB SDK Function
---

# token_decimals

## crypto_onchain_ethplorer_model.get_token_decimals

```python title='openbb_terminal/cryptocurrency/onchain/ethplorer_model.py'
def get_token_decimals(address: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethplorer_model.py#L176)

Description: Helper methods that gets token decimals number. [Source: Ethplorer]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | Blockchain balance e.g. 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984 | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | DataFrame with list of tokens and their balances. |

## Examples

