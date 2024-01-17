---
title: COMMERCIAL_PAPER
description: Learn about commercial paper, a form of short-term promissory notes issued
  primarily by corporations. Discover how it can help raise cash for current transactions
  and serve as a lower-cost alternative to bank loans. Explore the parameters and
  data returned by the commercial paper API endpoint.
keywords: 
- commercial paper
- short-term promissory notes
- corporations
- raise cash
- lower-cost alternative
- start_date
- end_date
- maturity
- category
- grade
- provider
- results
- warnings
- chart
- metadata
- data
- date
- rate
---

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="FIXEDINCOME.CORPORATE.COMMERCIAL_PAPER | OpenBB Add-in for Excel Docs" />

Commercial Paper.  Commercial paper (CP) consists of short-term, promissory notes issued primarily by corporations. Maturities range up to 270 days but average about 30 days. Many companies use CP to raise cash needed for current transactions, and many find it to be a lower-cost alternative to bank loans.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.COMMERCIAL_PAPER([start_date];[end_date];[maturity];[category];[grade];[provider])
```

### Example

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.COMMERCIAL_PAPER()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| maturity | Text | The maturity. | False |
| category | Text | The category. | False |
| grade | Text | The grade. | False |
| provider | Text | Options: fred, defaults to fred. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | Commercial Paper Rate.  |
