---
title: levels
description: This documentation page explains the 'levels' command used to retrieve
  the biggest levels for all prints over the last x days for a particular stock ticker.
  It provides its usage, parameters, and examples to help enhance your stock assessment.
keywords:
- Levels Command
- Stock Ticker
- Print levels
- Stock Performance
- Stock Assessment
- Documentation
- Command
- Parameters
- Examples
- Stock Information
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="darkpool: levels - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the Biggest Levels for All Prints over the last x days for the given ticker. This information is useful in assessing the overall performance of the stock, as it provides information on the largest levels of prints over the last x days.

### Usage

```python wordwrap
/levels ticker days
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| days | Number of days to look back | False | None |


---

## Examples

```
/levels TSLA 10
```

---
