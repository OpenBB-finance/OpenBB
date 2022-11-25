---
title: create
description: OpenBB Terminal Function
---

# create



### Usage

```python
create [-a {buy,sell}] (-prod PRODUCT | -sym SYMBOL) -p PRICE (-s SIZE | -up UP_TO) [-d {gtd,gtc}] [-t {limit,market,stop-limit,stop-loss}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| action | Action wanted. | buy | True | buy, sell |
| product | Id of the product wanted. | None | True | None |
| symbol | Symbol wanted. | None | True | None |
| price | Price wanted. | None | False | None |
| size | Price wanted. | None | True | None |
| up_to | Up to price. | None | True | None |
| duration | Duration of the Order. | gtd | True | gtd, gtc |
| type | Type of the Order. | limit | True | limit, market, stop-limit, stop-loss |

---
