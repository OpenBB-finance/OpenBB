---
title: fipo
description: This documentation page provides information and examples on using the
  'fipo' function, a tool for retrieving future IPO date estimates from financial
  data source Finnhub.io. This aids users in planning for upcoming IPOs by providing
  essential details such as exchange name, company name, number of shares, expected
  price, status, and total share value.
keywords:
- IPO
- Stock market
- future IPO dates
- SMART FOR LIFE, INC.
- NASDAQ Capital
- FinTech
- Finnhub.io
- Stock exchange
- Investment
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/disc/fipo - Reference | OpenBB Terminal Docs" />

Future IPOs dates. [Source: https://finnhub.io]

### Usage

```python
fipo [-d DAYS] [-s END] [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| days | Number of days in the future to look for IPOs. | 5 | True | None |
| end | The end date (format YYYY-MM-DD) to look for IPOs, starting from today. When set, end date will override --days argument | None | True | None |
| limit | Limit number of IPOs to display. | 20 | True | None |


---

## Examples

```python
2022 Feb 16, 03:59 (🦋) /stocks/disc/ $ fipo
                                                       Future IPO Dates
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Future     ┃ Exchange       ┃ Name                 ┃ Number of Shares ┃ Price      ┃ Status   ┃ symbol ┃ Total Shares Value ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ 2022-02-16 │ NASDAQ Capital │ SMART FOR LIFE, INC. │ 1800000          │ 9.00-11.00 │ expected │ SMFL   │ 22770000           │
└────────────┴────────────────┴──────────────────────┴──────────────────┴────────────┴──────────┴────────┴────────────────────┘
```
---
