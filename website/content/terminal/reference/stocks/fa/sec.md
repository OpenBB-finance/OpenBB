---
title: sec
description: Prints SEC filings of the company
keywords:
- stocks.fa
- sec
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /fa/sec - Reference | OpenBB Terminal Docs" />

Prints SEC filings of the company. The following fields are expected: Filing Date, Document Date, Type, Category, Amended, and Link. [Source: Market Watch and FinancialModelingPrep]

### Usage

```python wordwrap
sec [-t TICKER] [-l LIMIT] [-y YEAR] [-f {annual,quarterly,proxies,insiders,8-K,registrations,comments}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| ticker | -t  --ticker | The ticker to be used to get SEC filings. | AAPL | True | None |
| limit | -l  --limit | number of latest SEC filings. | 20 | True | None |
| year | -y  --year | year of SEC filings. | None | True | None |
| form | -f  --form | form group of SEC filings. | None | True | annual, quarterly, proxies, insiders, 8-K, registrations, comments |

---
