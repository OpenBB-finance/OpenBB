---
title: limitgtc
description: OpenBB Terminal Function
---

# market

Place a limit GTC order with Coinbase Advanced

### Usage

```python
limitgtc [--dry_run {True,False}] [--product_id PRODUCT_ID] [--side {BUY,SELL}] [--limit_price LIMIT_PRICE] [--base_size BASE_SIZE]
                [--post_only {True,False}] [-h] [--export EXPORT]
```

---

## Parameters

| Name        | Description                                                     | Default | Optional | Choices     |
|-------------|-----------------------------------------------------------------|---------|----------|-------------|
| dry_run     | Show the JSON payload to the API without placing the order.     | False   | True     | True, False |
| product_id  | Valid Coinbase Advanced product id pair (COIN-COIN or COIN-USD) | None    | False    | None        |
| side        | Transaction side                                                | None    | False    | BUY, SELL   |
| limit_price | Ceiling price for which the order should get filled.            | 0       | False    | None        |
 | base_size   | Amount of base currency to spend on order.                      | 0       | False    | None        |
 | post_only   | Post only limit order                                           | True    | False    | True, False |
---
