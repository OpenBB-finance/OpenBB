---
title: market
description: OpenBB Terminal Function
---

# market

Place a Market value order

### Usage

```python
market [--dry_run {True,False}] [--product_id PRODUCT_ID] [--side {BUY,SELL}] [--quote_size QUOTE_SIZE] [-b BASE_SIZE] [-h]
              [--export EXPORT]
```

---

## Parameters

| Name       | Description                                                     | Default | Optional                 | Choices     |
|------------|-----------------------------------------------------------------|---------|--------------------------|-------------|
| dry_run    | Show the JSON payload to the API without placing the order.     | False   | True                     | True, False |
| product_id | Valid Coinbase Advanced product id pair (COIN-COIN or COIN-USD) | None    | False                    | None        |
| side       | Transaction side                                                | None    | False                    | BUY, SELL   |
| quote_size | Amount of quote currency to spend on order.                     | None    | Required for BUY orders  | None        |
| base_size  | Amount of base currency to spend on order.                      | None    | Required for SELL orders | None        |
---
