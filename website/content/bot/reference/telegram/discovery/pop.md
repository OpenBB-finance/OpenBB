---
title: pop
description: The 'pop' command on OpenBB Bot allows users to retrieve the top 15 most
  popular stock tickers for the day or hour, providing an overview of current market
  trends.
keywords:
- pop command
- OpenBB Bot
- popular stocks
- 1 Hour stocks
- 1 Day stocks
- top 15 tickers
- stock market
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="discovery: pop - Telegram Reference | OpenBB Bot Docs" />

This command retrieves the top 15 tickers for the day or hour based on popularity on the OpenBB Bot across all our platforms. It allows users to get an overview of the most popular stocks in the market within the last 24 hours (1d) or 1 Hour (1hr).

### Usage

```python wordwrap
/pop interval
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| interval | Interval to filter by. `1hr`: "1 Hour", `1d`: "1 Day", | False | 1hr, 1d |


---

## Examples

```
/pop 1hr
```

---
