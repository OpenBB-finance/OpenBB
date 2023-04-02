---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: sumexp
description: OpenBB Discord Command
---

# sumexp

This command allows users to view the summary of all Flow options contracts for the specified ticker (AMD in this case) that expire on the specified date (2022-07-29 in this case). It provides the user with a comprehensive overview of the Flow options contracts, including the total open interest (OI) across all strikes, the underlying price, the total OI change over the past 24 hours, and the highest bid/ask spread.

### Usage

```python wordwrap
/flow sumexp ticker expiry
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date | False | None |


---

## Examples

```
/flow sumexp ticker:AMD expiry:2022-07-29
```

---
