---
title: pm
description: The 'pm' command is a tool that retrieves premarket data about a certain
  stock ticker. It gives information about the stock's latest price, the premarket
  change and the premarket percentage change.
keywords:
- pm command
- premarket data
- stock ticker
- stock price
- premarket change
- market opens
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duediligence: pm - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve premarket data for a given stock ticker. It will fetch the latest price, the premarket change, and the premarket percentage change of the selected stock. This is useful for those who want to get an idea of the stock's performance before the regular market opens.

### Usage

```python wordwrap
/pm ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/pm AMD
```

---
