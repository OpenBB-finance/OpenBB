---
title: fgdp
description: Forecast is based on an assessment of the economic climate in individual countries and the world economy, using a combination of model-based analyses and expert judgement
keywords:
- economy
- fgdp
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy /fgdp - Reference | OpenBB Terminal Docs" />

Forecast is based on an assessment of the economic climate in individual countries and the world economy, using a combination of model-based analyses and expert judgement. This indicator is measured in growth rates compared to previous year.

### Usage

```python wordwrap
fgdp [-c COUNTRIES] [-t {real,nominal}] [-q] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| countries | -c  --countries | Countries to get data for | united_states | True | None |
| types | -t  --types | Use either 'real' or 'nominal' | real | True | real, nominal |
| quarterly | -q  --quarterly | Whether to plot quarterly results. | False | True | None |
| start_date | -s  --start | Start date of data, in YYYY-MM-DD format | 2013-11-21 | True | None |
| end_date | -e  --end | End date of data, in YYYY-MM-DD format | 2033-11-21 | True | None |

---
