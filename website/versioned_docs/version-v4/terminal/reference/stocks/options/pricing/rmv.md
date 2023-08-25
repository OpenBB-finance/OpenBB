---
title: rmv
description: OpenBB Terminal Function
---

# rmv

Removes a price from the list

### Usage

```python
rmv -p PRICE [-a]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| price | Price you want to remove from the list | None | False | None |
| all | Remove all prices from the list | False | True | None |


---

## Examples

```python
2022 Feb 16, 09:44 (🦋) /stocks/options/pricing/ $ rmv -p 165

2022 Feb 16, 09:44 (🦋) /stocks/options/pricing/ $ show
Estimated price(s) of AAPL at 2022-05-20
┏━━━━━━━━┳━━━━━━━━┓
┃ Price  ┃ Chance ┃
┡━━━━━━━━╇━━━━━━━━┩
│ 175.00 │ 0.50   │
└────────┴────────┘
```
---
