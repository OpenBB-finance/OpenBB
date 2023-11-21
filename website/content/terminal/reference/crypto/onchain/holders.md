---
title: holders
description: Detailed guide on how to display top ERC20 token holders using python,
  with the option of sorting the data in various ways.
keywords:
- ERC20 token holders
- Ethplorer
- parameters
- sortby
- limit
- reverse
- data sorting
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /onchain/holders - Reference | OpenBB Terminal Docs" />

Display top ERC20 token holders: e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 [Source: Ethplorer]

### Usage

```python wordwrap
holders [-l LIMIT] [-s {balance,share}] [-r]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| limit | -l  --limit | display N number records | 10 | True | None |
| sortby | -s  --sort | Sort by given column. Default: share | share | True | balance, share |
| reverse | -r  --reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
