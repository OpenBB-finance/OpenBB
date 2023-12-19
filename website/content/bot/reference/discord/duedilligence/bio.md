---
title: bio
description: This page provides information about 'bio' command that fetches a stock's
  company info such as name, description, sector, industry, CEO, etc. using a stock
  ticker.
keywords:
- bio command
- stock's company info
- stock ticker
- stock information
- company's name
- company's description
- company's sector
- company's industry
- company's CEO
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duedilligence: bio - Discord Reference | OpenBB Bot Docs" />

This command retrieves a stock's company information and displays it to the user. It takes a stock ticker as an argument and returns information such as the company's name, description, sector, industry, CEO, and more.

### Usage

```python wordwrap
/dd bio ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/dd bio ticker:AMD
```
---
