---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: topstrikevol
description: OpenBB Discord Command
---

# topstrikevol

This command allows the user to retrieve an option strike volume breakdown for a given security (ticker: AMD in this example) with the ability to add an expiration date for a more detailed breakdown. The command is written in Python, using the wordwrap/op topstrikevol command.

### Usage

```python wordwrap
/op topstrikevol ticker [expiry]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date (optional) | True | None |


---

## Examples

```python wordwrap
/op topstrikevol ticker:AMD
```

---
