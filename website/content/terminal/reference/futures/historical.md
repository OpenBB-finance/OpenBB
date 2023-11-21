---
title: historical
description: This documentation page provides the user with instructions on how to
  display futures historical data. Certain parameters like ticker data, start date,
  and expiry date can be specified to customize the output according to individual
  needs.
keywords:
- display futures historical
- futures timeseries
- Ticker data
- historical data
- future expiry date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="futures /historical - Reference | OpenBB Terminal Docs" />

Display futures historical. [Source: YahooFinance]

### Usage

```python wordwrap
historical -t TICKER [-s START] [-e END] [--expiry EXPIRY]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| ticker | -t  --ticker | Future ticker to display timeseries separated by comma when multiple, e.g.: BLK,QI |  | False | None |
| start | -s  --start | Initial date. Default: 2 years ago | datetime.now() - timedelta(days=365) | True | None |
| end | -e  --end | Final date. Default: today | datetime.now() | True | None |
| expiry | --expiry | Select future expiry date with format YYYY-MM |  | True | None |

![blk](https://user-images.githubusercontent.com/25267873/196562549-1251b0fd-ca36-4e0f-bca6-b6bfe473effa.png)

![Figure_31](https://user-images.githubusercontent.com/25267873/196562627-79f9ffa1-8582-457c-91e8-5c18d6d4304f.png)

---
