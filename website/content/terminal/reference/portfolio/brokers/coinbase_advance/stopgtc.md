---
title: stopgtc
description: OpenBB Terminal Function
---

# market

Place a stop GTC order with Coinbase Advanced

### Usage

```python
stopgtc [--dry_run {True,False}] [--product_id PRODUCT_ID] [--side {BUY,SELL}] [--limit_price LIMIT_PRICE] [--stop_price STOP_PRICE]
               [--base_size BASE_SIZE] [--stop_direction {STOP_DIRECTION_STOP_UP,STOP_DIRECTION_STOP_DOWN}] [-h] [--export EXPORT]
```

---

## Parameters

| Name           | Description                                                                                                                                                                                                         | Default | Optional | Choices                                         |
|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|----------|-------------------------------------------------|
| dry_run        | Show the JSON payload to the API without placing the order.                                                                                                                                                         | False   | True     | True, False                                     |
| product_id     | Valid Coinbase Advanced product id pair (COIN-COIN or COIN-USD)                                                                                                                                                     | None    | None     | None                                            |
| side           | Transaction side                                                                                                                                                                                                    | None    | False    | BUY, SELL                                       |
| limit_price    | Ceiling price for which the order should get filled.                                                                                                                                                                | 0       | False    | None                                            |
 | base_size      | Amount of base currency to spend on order.                                                                                                                                                                          | 0       | False    | None                                            |
 | stop_price     | Price at which the order should trigger - if stop direction is Up, then the order will trigger when the last trade price goes above this, otherwise order will trigger when last trade price goes below this price. | 0       | False    | None                                            |
 | stop_direction | Stop direction                                                                                                                                                                                                      | None    | False    | STOP_DIRECTION_STOP_UP,STOP_DIRECTION_STOP_DOWN |
---
