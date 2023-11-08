---
title: insiders
description: This page provides information about retrieving insider transactions
  for a given stock. It explains the /insiders command usage, parameters and provides
  examples
keywords:
- insider transactions
- stock data
- stock ticker
- buy/sell transactions
- average price
- /insiders command
- command usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="duediligence: insiders - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the 15 most recent insider transactions for a given stock. It will provide information such as the date of the transaction, the company insider involved, the number of shares traded, the type of transaction (buy/sell), and the average price of the transaction.

### Usage

```python wordwrap
/insiders ticker
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |


---

## Examples

```
/insiders AMD
```

---
