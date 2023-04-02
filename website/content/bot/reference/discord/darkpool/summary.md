---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: summary
description: OpenBB Discord Command
---

# summary

This command retrieves a summary of all the prints by percentage of MarketCap over the last x days, sorted by MarketCap. The summary includes the total number of prints and their total percentage of MarketCap, as well as the float and short percentage.

### Usage

```python wordwrap
/dp summary days sort
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
/dp summary days:10 sort:MarketCap
```

---
