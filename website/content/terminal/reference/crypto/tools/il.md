---
title: il
description: The Document page provides details on the 'il' tool designed to calculate
  Impermanent Loss in custom liquidity pools. Including its usage, and parameters
  such as token price change and pool proportion, the tool allows users to estimate
  potential impermanent losses.
keywords:
- Impermanent Loss
- Liquidity Pool
- Token Price Change
- Pool Proportion
- Dollar Value
- il Tool
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/tools/il - Reference | OpenBB Terminal Docs" />

Tool to calculate Impermanent Loss in a custom liquidity pool. Users can provide percentages increases for two tokens (and their weight in the liquidity pool) and verify the impermanent loss that can occur.

### Usage

```python
il [-a PRICECHANGEA] [-b PRICECHANGEB] [-p PROPORTION] [-v VALUE] [-n]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| priceChangeA | Token A price change in percentage | 0 | True | range(1, 101) |
| priceChangeB | Token B price change in percentage | 100 | True | range(1, 101) |
| proportion | Pool proportion. E.g., 50 means that pool contains 50%% of token A and 50%% of token B, 30 means that pool contains 30%% of token A and 70%% of token B | 50 | True | range(1, 101) |
| value | Initial amount of dollars that user provides to liquidity pool | 1000 | True | None |
| narrative | Flag to show narrative instead of dataframe | False | True | None |

---
