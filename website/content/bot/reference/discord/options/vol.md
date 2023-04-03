---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: vol
description: OpenBB Discord Command
---

# vol

This command allows the user to retrieve a chart of Options Volume by Strike for a specified ticker. This data can be broken down further by adding an expiration date for a more detailed breakdown.

### Usage

```python wordwrap
/op vol ticker [expiry]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date (optional) | True | None |


---

## Examples

```
/op vol ticker:AMD
```

```
/op vol ticker:AMD expiry:2022-07-29
```

---
