---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: defi
description: OpenBB Telegram Command
---

# defi

This command will retrieve a chart or table of the top DeFi protocols by market capitalization. It will provide a visual representation of the relative size of each protocol, as well as an overview of the total DeFi market size. This will enable users to get a better understanding of the current DeFi landscape and identify which protocols are leading the way.

### Usage

```python wordwrap
/defi [sortby] [chain] [reverse] [chart]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| sortby | Column to sort data by (e.g., tvl) | True | tvl, mc, 1hr, 1d, 1wk |
| chain | Chain to filter by (e.g., ethereum) | True | None |
| reverse | Reverse the sort order (e.g., True) (default: False) | True | None |
| chart | Show chart (e.g., True) (default: False) | True | None |


---

## Examples

```
/defi chart
```

---
