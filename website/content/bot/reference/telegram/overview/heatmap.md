---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: heatmap
description: OpenBB Telegram Command
---

# heatmap

Daily Heat Maps by Market. Sector is optional.

### Usage

```python wordwrap
/heatmap market [sector]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| market | Market to filter by. `sp500`: "S&P 500", `nasdaq100`: "NASDAQ 100", `iwm2000`: "Russell 2000", `iwb1000`: "Russell 1000", `dow30`: "Dow Jones 30", `crypto`: "Crypto" | False | sp500, nasdaq100, iwm2000, iwb1000, dow30, crypto |
| sector | Sector to filter by. If not specified, all sectors are returned. `1`: "Basic Materials" `2`: "Conglomerates" `3`: "Consumer Goods" `4`: "Financial" `5`: "Healthcare" `6`: "Industrial Goods" `7`: "Services" `8`: "Technology" `9`: "Utilities" | True | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 |


---

## Examples

```
/heatmap sp500
```

```
/heatmap sp500 services
```
---
