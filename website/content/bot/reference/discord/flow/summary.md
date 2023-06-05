---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: summary
description: OpenBB Discord Command
---

# summary

This command allows the user to retrieve a summary of all the flow per stock over the last x days, with the result sorted in various ways. This summary will include the ratio to total market capitalization, the number of trades, and other information.

### Usage

```python wordwrap
/flow summary days sort
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| days | Number of days to look back | False | None |
| sort | Sort by MarketCap, Float, Total, or Short Percentage | False | MarketCap (mc), Float (float), Total (sum), Short Percentage (short) |


---

## Examples

```
/flow summary days:5 sort:Float
```

```
/flow summary days:5 sort:Short Percentage
```

---
