---
title: sales
description: Select the postcode you want to see sold house price data for
keywords:
- alt.realestate
- sales
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt /realestate/sales - Reference | OpenBB Terminal Docs" />

Select the postcode you want to see sold house price data for. [Source: UK Land Registry]

### Usage

```python wordwrap
sales -p postcode [-l limit]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| postcode | -p  --postcode | Postcode | None | False | None |
| limit | -l  --limit | Number of entries to return | 25 | True | None |

---
