---
title: exp
description: Detailed guide on the 'flowsum exp' command used for retrieving the total
  premium of a given stock ticker for the current trading day, including example usage
  and parameters explanation.
keywords:
- flowsum exp command
- option premium
- stock ticker
- trading day
- above ask
- expiry
- expiration date
- 'subcmd: exp'
- example usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="flowsum - flow: exp - Telegram Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the total premium of the given stock ticker for the current trading day by expiration. We categorize the calls and puts by where the trade occurred on the bid/ask. For example, Above Ask, means the trade happened over the current Ask price.

### Usage

```python wordwrap
/flowsum exp [ticker] [expiry]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker - Not available for subcmd: top | True | None |
| expiry | Expiration date - Only available/required for subcmd: exp | True | None |


---

## Examples

```
/flowsum exp AMD 2022-07-29
```

---
