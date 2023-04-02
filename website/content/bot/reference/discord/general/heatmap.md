---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: heatmap
description: OpenBB Discord Command
---

# heatmap

?

This command allows the user to retrieve Daily Heat Maps by Market. The user must specify the market they are interested in, in this case the S&P 500. The sector is optional and can be used to narrow down the search. The Daily Heat Maps will be provided to the user in response to the command.

### Usage

```python wordwrap
/heatmap market [sector]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| market | Market to filter by. | False | S&P 500 (sp500), NASDAQ 100 (nasdaq100), Russell 2000 (iwm2000), Russell 1000 (iwb1000), Dow Jones 30 (dow30), Crypto (crypto) |
| sector | Sector to filter by. If not specified, all sectors are returned. | True | Basic Materials (1), Conglomerates (2), Consumer Goods (3), Financial (4), Healthcare (5), Industrial Goods (6), Services (7), Technology (8), Utilities (9) |


---

## Examples

```
/heatmap market:S&P 500
```
```
/heatmap market:S&P 500 sector:Services
```

---
