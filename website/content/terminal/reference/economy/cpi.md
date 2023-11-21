---
title: cpi
description: Plot (harmonized) consumer price indices for a variety of countries and regions
keywords:
- economy
- cpi
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /cpi - Reference | OpenBB Terminal Docs" />

Plot (harmonized) consumer price indices for a variety of countries and regions.

### Usage

```python wordwrap
cpi [-c COUNTRIES] [-u {growth_previous,growth_same,index_2015}] [--frequency {monthly,quarterly,annual}] [--harmonized] [--no-smart-select] [-o] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| countries | -c  --countries | What countries you'd like to collect data for | united_states | True | None |
| units | -u  --units | What units you'd like to collect data for | growth_same | True | growth_previous, growth_same, index_2015 |
| frequency | --frequency | What frequency you'd like to collect data for | monthly | True | monthly, quarterly, annual |
| harmonized | --harmonized | Whether to use harmonized cpi data | False | True | None |
| smart_select | --no-smart-select | Whether to assist with selection | True | True | None |
| options | -o  --options | See the available options | False | True | None |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | 1993-11-21 | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | 2023-11-21 | True | None |

---
