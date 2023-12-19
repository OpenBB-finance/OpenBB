---
title: sumweek
description: Explore how the sumweek command allows the user to view the most prevalent
  option flows for a given stock over a week. Understand market sentiment with this
  tool.
keywords:
- sumweek command
- stock market
- market sentiment
- option flow
- stock ticker
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flow: sumweek - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the top flow for the week for Calls and Puts by stock. This will provide the user with an overview of the market's current sentiment towards a particular stock as well as an overall view of the market's sentiment towards all stocks.

### Usage

```python wordwrap
/flow sumweek ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/flow sumweek ticker:AMD
```

---
