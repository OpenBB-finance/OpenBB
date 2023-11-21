---
title: tipt
description: The page provides an overview and usage of the 'tipt' function, a tool
  that prints the top insider purchases of the day from OpenInsider. With parameter
  customization and examples, become more adept at monitoring insider stock purchases.
keywords:
- tipt function
- insider purchases
- OpenInsider
- stock
- stock monitoring
- stock analysis
- guide
- usage
- tutorial
- data display
- trade
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ins/tipt - Reference | OpenBB Terminal Docs" />

Print top insider purchases of the day. [Source: OpenInsider]

### Usage

```python
tipt [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of datarows to display | 10 | True | None |


---

## Examples

```python
2022 Feb 16, 08:18 (🦋) /stocks/ins/ $ tipt
                                                                          Insider Data
┏━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ X ┃ Filing Date ┃ Trade Date ┃ Ticker ┃ Company Name     ┃ Insider Name         ┃ Title    ┃ Trade Type   ┃ Price ┃ Qty     ┃ Owned   ┃ Diff Own ┃ Value     ┃
┡━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ M │ 2022-02-16  │ 2022-02-09 │ ZIVO   │ Zivo Bioscience, │ Maggiore Christopher │ Dir, 10% │ P - Purchase │ $3.72 │ +91,334 │ 803,105 │ +13%     │ +$340,098 │
│   │ 06:02:09    │            │        │ Inc.             │ D.                   │          │              │       │         │         │          │           │
└───┴─────────────┴────────────┴────────┴──────────────────┴──────────────────────┴──────────┴──────────────┴───────┴─────────┴─────────┴──────────┴───────────┘
M: Multiple transactions in filing; earliest reported transaction date & weighted average transaction price
```
---
