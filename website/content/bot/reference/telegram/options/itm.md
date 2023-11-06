---
title: itm
description: The page provides detailed instructions on using the 'itm' command to
  retrieve a list of In-the-Money options for a given stock ticker symbol. The command
  compares and delivers a total of In-the-Money and Out-the-Money Calls and Puts.
keywords:
- In-the-Money options
- stock ticker symbol
- expiry date
- Calls and Puts
- Out-the-Money
- options retrieval command
- python command
- stock ticker
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: itm - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a list of In-the-Money options for the stock ticker symbol sorted by expiry date. The command compares the amount of Calls and Puts In-the-Money vs Out-the-Money and gives a total.

### Usage

```python wordwrap
/itm ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/itm AMD
```

---
