---
title: token_decimals
description: OpenBB SDK Function
---

# token_decimals

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

