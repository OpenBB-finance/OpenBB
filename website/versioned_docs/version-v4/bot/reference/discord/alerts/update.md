---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: update
description: OpenBB Discord Command
---

# update

This command allows the user to update the condition on an active alert, such as changing the value of a price alert. The command will update the alert with the new condition and keep the alert active until it is manually deactivated or the alert's condition is met.

### Usage

```python wordwrap
/alerts update alerts condition price
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| alerts | Your active alerts | False | None |
| condition | Update condition for alert | False | Equal or Above (above or equal), Equal or Below (below or equal) |
| price | Update alert to this price | False | None |


---

## Examples

```
/alerts update alerts: condition: price:
```

---
