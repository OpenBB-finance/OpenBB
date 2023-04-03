---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: chains
description: OpenBB Discord Command
---

# chains

This command allows users to retrieve Options Chain by Expiry, which gives an overview of the bid, ask, and open interest of options contracts for a specific stock.

### Usage

```python wordwrap
/op chains ticker expiry opt_type [min_sp] [max_sp]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date | False | None |
| opt_type | Calls or Puts | False | Calls, Puts |
| min_sp | Minimum Strike Price | True | None |
| max_sp | Maximum Strike Price | True | None |


---

## Examples

```
/op chains ticker:AMD expiry:2022-07-29 opt_type:Calls
```

```
/op chains ticker:AMD expiry:2022-07-29 opt_type:Calls min_sp:10 max_sp:100
```

---
