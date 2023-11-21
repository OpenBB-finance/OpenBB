---
title: wk
description: This page provides the documentation of `flowsum wk` command. It explains
  how to retrieve the top flow per week for Calls and Puts by stock for understanding
  the market's sentiment towards a certain stock. Parameters and usage are
  clearly detailed.
keywords:
- flowsum wk
- stock market sentiment
- Put and Call analysis
- top flow retrieval
- stock ticker
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flowsum - flow: wk - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the top flow for the week for Calls and Puts by stock. This will provide the user with an overview of the market's current sentiment towards a particular stock as well as an overall view of the market's sentiment towards all stocks.

### Usage

```python wordwrap
/flowsum wk [ticker]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker - Not available for subcmd: top | True | None |


---

## Examples

```
/flowsum wk AMD
```
---
