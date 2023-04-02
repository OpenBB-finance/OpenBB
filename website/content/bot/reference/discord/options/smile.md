---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: smile
description: OpenBB Discord Command
---

# smile

This command allows the user to retrieve the Display Options Volatility Smile for the given ticker (AMD) and expiry (2022-07-29). The Display Options Volatility Smile is a graphical representation of the implied volatility for a given option that can be used to gauge the market sentiment for a particular security. The Volatility Smile allows the user to get a better understanding of the options market and make more informed trading decisions.

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
