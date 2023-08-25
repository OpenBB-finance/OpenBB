---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: smile
description: OpenBB Telegram Command
---

# smile

This command allows the user to retrieve the Options Volatility Smile for the given ticker and expiry. The Options Volatility Smile is a graphical representation of the implied volatility for a given option that can be used to gauge the market sentiment for a particular security.

### Usage

```python wordwrap
/smile ticker expiry [min_sp] [max_sp]
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
/smile AMD 2022-07-29
```
```
/smile AMD 2022-07-29 10 100
```
---
