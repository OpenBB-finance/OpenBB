---
title: search
description: OpenBB Terminal Function
---

# search

Search futures. [Source: YahooFinance]

### Usage

```python
search [-e {NYB,CMX,CME,CBT,NYM}] [-c {metals,agriculture,index,hydrocarbon,bonds,currency}] [-d DESCRIPTION [DESCRIPTION ...]]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| exchange | Select the exchange where the future exists |  | True | NYB, CMX, CME, CBT, NYM |
| category | Select the category where the future exists |  | True | metals, agriculture, index, hydrocarbon, bonds, currency |
| description | Select the description future you are interested in |  | True | None |

---
