# Headless Oracle Provider

This provider exposes signed market-state receipts from Headless Oracle for OpenBB.

## Supported models

- `MarketState`

## Example

```python
from openbb import obb

obb.equity.market_state(exchange="XNYS", provider="headless_oracle")
```
