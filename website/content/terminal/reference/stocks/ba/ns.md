---
title: ns
description: Shows the News Sentiment articles data
keywords:
- stocks.ba
- ns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /ba/ns - Reference | OpenBB Terminal Docs" />

Shows the News Sentiment articles data

### Usage

```python wordwrap
ns [-t TICKER] [-s START_DATE] [-e END_DATE] [-d DATE] [-l LIMIT] [-o OFFSET]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| ticker | -t  --ticker | Ticker to search for. | None | True | None |
| start_date | -s  --start_date | The starting date (format YYYY-MM-DD) to search news articles from | None | True | None |
| end_date | -e  --end_date | The end date (format YYYY-MM-DD) to search news articles upto | None | True | None |
| date | -d  --date | Shows the news articles data on this day (format YYYY-MM-DD). If you use this Argument start date and end date will be ignored | None | True | None |
| limit | -l  --limit | Number of news articles to be displayed. | 10 | True | None |
| offset | -o  --offset | offset indicates the starting position of news articles. | 0 | True | None |

---
