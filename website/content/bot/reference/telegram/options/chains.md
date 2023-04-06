---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: chains
description: OpenBB Telegram Command
---

# chains

Displays Options Chain by Expiry.

### Usage

```python wordwrap
/chains ticker expiry opt_type [min_sp] [max_sp]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date (YYYY-MM-DD) | False | None |
| opt_type | Calls or Puts (C or P) | False | calls, puts, C, P |
| min_sp | Minimum Strike Price | True | None |
| max_sp | Maximum Strike Price | True | None |


---

## Examples

```
/chains AMD 2022-07-29 Calls
```
```
/chains AMD 2022-07-29 Calls 10 100
```

---
