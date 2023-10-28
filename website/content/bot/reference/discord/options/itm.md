---
title: itm
description: A comprehensive guide on the 'itm' command that helps to acquire In-the-Money
  options for chosen stock ticker.
keywords:
- itm command
- In-the-Money options
- stock ticker
- Calls and Puts
- Out-the-Money options
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: itm - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve a list of In-the-Money options for the stock ticker symbol sorted by expiry date. The command compares the amount of Calls and Puts In-the-Money vs Out-the-Money and gives a total.

### Usage

```python wordwrap
/op itm ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/op itm ticker:AMD
```

---
