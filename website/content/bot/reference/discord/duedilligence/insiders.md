---
title: insiders
description: The Insiders page allows users to retrieve the 15 most recent insider
  transactions for a given stock, including the date of the transaction, the insider
  involved, the number of shares traded, the type of transaction, and the average
  price. You can run this command by entering '/dd insiders ticker:<ticker>'.
keywords:
- insiders command
- recent insider transactions
- stock information
- shares traded
- transaction type
- average price
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duedilligence: insiders - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the 15 most recent insider transactions for a given stock. It will provide information such as the date of the transaction, the company insider involved, the number of shares traded, the type of transaction (buy/sell), and the average price of the transaction.

### Usage

```python wordwrap
/dd insiders ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/dd insiders ticker:AMD
```
---
