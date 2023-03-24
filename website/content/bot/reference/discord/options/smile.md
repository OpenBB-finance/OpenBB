---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: smile
description: OpenBB Discord Command
---

# smile

Displays Options Volatility Smile.

### Usage

```python wordwrap
/op smile ticker expiry [min_sp] [max_sp]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date | False | None |
| min_sp | Minimum Strike Price | True | None |
| max_sp | Maximum Strike Price | True | None |


---

## Examples

```
/op smile ticker:AMD expiry:2022-07-29
```

```
/op smile ticker:AMD expiry:2022-07-29 min_sp:10 max_sp:100
```

---
