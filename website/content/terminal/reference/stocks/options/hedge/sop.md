---
title: sop
description: The sop command in this documentation demonstrates how to view selected
  options in a stock hedge. It provides usage, parameter details, and practical examples.
keywords:
- sop
- parameters
- options
- stocks
- hedge
- add
- implied volatility
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/hedge/sop /options - Reference | OpenBB Terminal Docs" />

Displays selected option

### Usage

```python
sop
```

---

## Parameters

This command has no parameters



---

## Examples

```python
2022 May 10, 09:34 (🦋) /stocks/options/hedge/ $ add 20
          Current Option Positions
┏━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Type ┃ Hold ┃ Strike ┃ Implied Volatility ┃
┡━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Call │ Long │ 142.00 │ 0.05               │
├──────┼──────┼────────┼────────────────────┤
│ Call │ Long │ 155.00 │ 0.06               │
└──────┴──────┴────────┴────────────────────┘
```
---
