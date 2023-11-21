---
title: alswe
description: A documentation page for the 'alswe' tool providing allocation insights
  for a Swedish fund. Includes parameters for focus on country, sector, or holding
  levels.
keywords:
- allocation
- swedish fund
- alswe
- fund exposure
- fund allocation
- sector
- country
- holding
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="funds /alswe - Reference | OpenBB Terminal Docs" />

Show allocation of a swedish fund. To get a list of available funds, check the file `avanza_fund_ID.csv`.

### Usage

```python wordwrap
alswe [--focus {all,country,sector,holding}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| focus | --focus | The focus of the funds exposure/allocation | all | True | all, country, sector, holding |

---
