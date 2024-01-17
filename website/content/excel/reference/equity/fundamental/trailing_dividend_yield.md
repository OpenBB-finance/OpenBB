---
title: TRAILING_DIVIDEND_YIELD
description: Trailing 1yr dividend yield
keywords: 
- equity
- fundamental
- trailing_dividend_yield
---

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="EQUITY.FUNDAMENTAL.TRAILING_DIVIDEND_YIELD | OpenBB Add-in for Excel Docs" />

Trailing 1yr dividend yield.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.TRAILING_DIVIDEND_YIELD([symbol];[provider])
```

### Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.TRAILING_DIVIDEND_YIELD()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: tiingo, defaults to tiingo. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| trailing_dividend_yield | Trailing dividend yield.  |
