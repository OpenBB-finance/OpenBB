---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: create
description: OpenBB Discord Command
---

# create

Create an alert with conditions for a symbol

### Usage

```python wordwrap
/alerts create ticker condition price
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Ticker to set alert for | False | None |
| condition | Condition to set alert for | False | Equal or Above, Equal or Below |
| price | Price to set alert for | False | None |


---

## Examples

```
/alerts create ticker:BTCUSD condition:Equal or Above price:1000
```

```
/alerts create ticker:SPY condition:Equal or Below price:400
```

---
