---
title: day
description: The documentation page is about the 'flowsum' command that allows users
  to retrieve the total premium of a given stock ticker on the current trading day.
  It provides examples and parameters of the command and explains the trade categorization
  on the bid/ask.
keywords:
- flowsum
- stock Ticker
- trade
- premium
- Above Ask
- current trading day
- bid/ask
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flowsum - flow: day - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the total premium of the given stock ticker for the current trading day. We categorize the calls and puts by where the trade occurred on the bid/ask. For example, Above Ask, means the trade happened over the current Ask price.

### Usage

```python wordwrap
/flowsum [ticker]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker - Not available for subcmd: top | True | None |


---

## Examples

```
/flowsum AMD
```

---
