---
title: rmv
description: This documentation page outlines the usage, parameters and examples for
  the rmv command in the hedge. With rmv, you can efficiently remove one of the options
  shown in the hedge or all of them.
keywords:
- rmv command
- hedge options
- remove option
- stocks options
- programming command
- command usage
- command parameters
- command examples
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /options/hedge/rmv - Reference | OpenBB Terminal Docs" />

Remove one of the options to be shown in the hedge.

### Usage

```python wordwrap
rmv [-o OPTION [OPTION ...]] [-a]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| option | -o  --option | index of the option to remove | None | True | None |
| all | -a  --all | remove all of the options | False | True | None |


---

## Examples

```python
2022 May 10, 09:32 (🦋) /stocks/options/hedge/ $ rmv Option A
          Current Option Positions           
┏━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Type ┃ Hold ┃ Strike ┃ Implied Volatility ┃
┡━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ Call │ Long │ 155.00 │ 0.06               │
└──────┴──────┴────────┴────────────────────┘
```
---
