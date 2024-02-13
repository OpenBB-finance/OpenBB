---
title: icespread
description: Plot various rates from the United States
keywords:
- fixedincome
- icespread
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /icespread - Reference | OpenBB Terminal Docs" />

Plot various rates from the United States. This includes tbill (Treasury Bills), Constant Maturity treasuries (cmn) and Inflation Protected Treasuries (TIPS)

### Usage

```python wordwrap
icespread [-c {all,duration,eur,usd}] [-a {asia,emea,eu,ex_g10,latin_america,us}] [-g {a,aa,aaa,b,bb,bbb,ccc,crossover,high_grade,high_yield,non_financial,non_sovereign,private_sector,public_sector}] [-o] [-d] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| category | -c  --category | What category you'd like to collect data for | all | True | all, duration, eur, usd |
| area | -a  --area | What region you'd like to collect data for | us | True | asia, emea, eu, ex_g10, latin_america, us |
| grade | -g  --grade | What grade you'd like to collect data for | non_sovereign | True | a, aa, aaa, b, bb, bbb, ccc, crossover, high_grade, high_yield, non_financial, non_sovereign, private_sector, public_sector |
| options | -o  --options | See the available options | False | True | None |
| description | -d  --description | Whether to provide a description of the data. | False | True | None |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | 1980-01-01 | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---
