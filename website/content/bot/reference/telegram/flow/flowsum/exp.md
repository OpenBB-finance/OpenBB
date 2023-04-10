---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: exp
description: OpenBB Telegram Command
---

# flowsum exp

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
