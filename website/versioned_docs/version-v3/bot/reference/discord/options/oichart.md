---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: oichart
description: OpenBB Discord Command
---

# oichart

This command allows users to retrieve a chart of Total Open Interest by Strike Price for the given ticker symbol. This chart provides a visual representation of the open interest on various strike prices for the given ticker symbol, where the size of each point on the graph reflects the amount of open interest. This can be used to analyze the open interest on various strike prices and make informed decisions about the underlying security.

### Usage

```python wordwrap
/op oichart ticker [expiry]
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
/op oichart ticker:AMD
```

```
/op oichart ticker:AMD expiry:2022-07-29
```

---
