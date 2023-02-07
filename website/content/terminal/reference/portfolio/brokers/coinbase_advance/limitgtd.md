---
title: limitgtd
description: OpenBB Terminal Function
---

# market

Place a limit GTD order with Coinbase Advanced

### Usage

```python
limitgtd [--dry_run {True,False}] [-p PRODUCT_ID] [-s {BUY,SELL}] [-l LIMIT_PRICE] [-b BASE_SIZE] [--post_only {True,False}]
                [-d END_TIME] [-h] [--export EXPORT]
```

---

## Parameters

| Name        | Description                                                                              | Default | Optional | Choices     |
|-------------|------------------------------------------------------------------------------------------|---------|----------|-------------|
| dry_run     | Show the JSON payload to the API without placing the order.                              | False   | True     | True, False |
| product_id  | Valid Coinbase Advanced product id pair (COIN-COIN or COIN-USD)                          | None    | False    | None        |
| side        | Transaction side                                                                         | None    | False    | BUY, SELL   |
| limit_price | Ceiling price for which the order should get filled.                                     | 0       | False    | None        |
 | base_size   | Amount of base currency to spend on order.                                               | 0       | False    | None        |
 | post_only   | Post only limit order                                                                    | True    | False    | True, False |
 | end_time    | Order valid until this Date-Time. Format DD-MM-YYYY_HH:MM_AM/PM important: no spaces (_) | None    | False    | None        |
---
