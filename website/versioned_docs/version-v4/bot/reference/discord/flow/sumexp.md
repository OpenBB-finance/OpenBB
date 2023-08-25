---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: sumexp
description: OpenBB Discord Command
---

# sumexp

This command allows the user to retrieve the total premium of the given stock ticker for the current trading day by expiration. We categorize the calls and puts by where the trade occurred on the bid/ask. For example, Above Ask, means the trade happened over the current Ask price.

### Usage

```python wordwrap
/flow sumexp ticker expiry
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date | False | None |


---

## Examples

```
/flow sumexp ticker:AMD expiry:2022-07-29
```

---
