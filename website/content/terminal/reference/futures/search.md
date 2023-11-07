---
title: search
description: A detailed guide on how to use the search feature in YahooFinance for
  futures. Learn how to choose different parameters like exchange, category and description
  for a more specific search.
keywords:
- YahooFinance Search
- Futures Search Tool
- YahooFinance Futures
- Search Exchange Futures
- Search Category Futures
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="futures /search - Reference | OpenBB Terminal Docs" />

Search futures. [Source: YahooFinance]

### Usage

```python
search [-e {NYB,CMX,CME,CBT,NYM}] [-c {metals,agriculture,index,hydrocarbon,bonds,currency}] [-d DESCRIPTION [DESCRIPTION ...]]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| exchange | Select the exchange where the future exists |  | True | NYB, CMX, CME, CBT, NYM |
| category | Select the category where the future exists |  | True | metals, agriculture, index, hydrocarbon, bonds, currency |
| description | Select the description future you are interested in |  | True | None |

---
