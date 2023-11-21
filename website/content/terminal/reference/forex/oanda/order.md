---
title: order
description: How to create an order, set unit and price, and understanding of long
  and short position in order request. Also, guides on setting the price for a limit
  order.
keywords:
- order
- units
- price
- long position
- short position
- limit order
- order request
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forex/oanda/order - Reference | OpenBB Terminal Docs" />

Create order

### Usage

```python
order -u UNITS -p PRICE
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| units | The number of units to place in the order request. Positive for a long position and negative for a short position. | None | False | None |
| price | The price to set for the limit order. | None | False | None |

---
