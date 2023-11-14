---
title: spread
description: 'Documentation page for ''spread'' software: a tool designed to generate
  bond spread matrix. This tool is parametrizable, allowing users to customize its
  outputs.'
keywords:
- spread software
- bond spread matrix
- financial tools
- bond spread matrix generator
- bond spread
- financial software
- customizable finance tool
- bond rates
- finance heatmap
- financial data visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /spread - Reference | OpenBB Terminal Docs" />

Generate bond spread matrix.

### Usage

```python
spread [-g {G7,PIIGS,EZ,AMERICAS,EUROPE,ME,APAC,AFRICA}] [-c COUNTRIES] [-m MATURITY] [--change CHANGE] [--color {rgb,binary,openbb}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| group | Show bond spread matrix for group of countries. | G7 | True | G7, PIIGS, EZ, AMERICAS, EUROPE, ME, APAC, AFRICA |
| countries | Show bond spread matrix for explicit list of countries. | None | True | None |
| maturity | Specify maturity to compare rates. | 10Y | True | None |
| change | Get matrix of 1 day change in rates or spreads. | False | True | None |
| color | Set color palette on heatmap. | openbb | True | rgb, binary, openbb |

---
