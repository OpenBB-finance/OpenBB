---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: oi
description: OpenBB Discord Command
---

# oi

This command allows the user to retrieve the Open Interest and Call/Put ratio for a given stock. Optionally, the user can also specify an expiration date to get a more granular breakdown.

### Usage

```python wordwrap
/op oi ticker [expiry]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date | True | None |


---

## Examples

```
/op oi ticker:AMC
```

```
/op oi ticker:AMC expiry:2022-07-29
```

---
