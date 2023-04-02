---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: day
description: OpenBB Discord Command
---

# day

This command retrieves the most recent flow for a stock with the specified ticker symbol. The command requires the user to input the ticker symbol of the stock they would like to get the most recent flow for, and will return the most up-to-date flow data for that stock.

### Usage

```python wordwrap
/flow day ticker [expiry] [strike] [opt_type]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiry Date (YYYY-MM-DD) (Optional) | True | None |
| strike | Strike Price (Optional) | True | None |
| opt_type | Option Type (Calls or Puts) (Optional) | True | Calls (C), Puts (P) |


---

## Examples

```
/flow day ticker:AMD
```

```
/flow day ticker:AMD expiry:2022-07-29 strike:60 opt_type:Puts
```

```
/flow day ticker:AMD expiry:2022-07-29 strike:60
```

---
