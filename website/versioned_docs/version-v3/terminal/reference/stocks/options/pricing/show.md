---
title: show
description: OpenBB Terminal Function
---

# show

Display prices

### Usage

```python
show
```

---

## Parameters

This command has no parameters



---

## Examples

```python
2022 Feb 16, 09:45 (🦋) /stocks/options/pricing/ $ add -p 100 -c 0.5

2022 Feb 16, 09:46 (🦋) /stocks/options/pricing/ $ add -p 200 -c 0.5

2022 Feb 16, 09:46 (🦋) /stocks/options/pricing/ $ show
Estimated price(s) of AAPL at 2022-05-20
┏━━━━━━━━┳━━━━━━━━┓
┃ Price  ┃ Chance ┃
┡━━━━━━━━╇━━━━━━━━┩
│ 100.00 │ 0.50   │
├────────┼────────┤
│ 200.00 │ 0.50   │
└────────┴────────┘
```
---
