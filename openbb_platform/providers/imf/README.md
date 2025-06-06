# OpenBB IMF Provider Extension

This package adds the `openbb-imf` provider extension to the OpenBB Platform.

## Installation

Install from PyPI with:

```sh
pip install openbb-imf
```

## Implementation

The extension utilizes the JSON RESTful Web Service ((https://datahelp.imf.org/knowledgebase/articles/630877-data-services)[https://datahelp.imf.org/knowledgebase/articles/630877-data-services])

No authorization is required to use, but IP addresses are bound by the limitations described in the link above.

## Coverage

- Databases:
  - International Reserves and Foreign Currency Liquidity
  - Direction of Trade Statistics
  - Financial Soundness Indicators
  - Port Watch

Coverage:
  - All IRFCL tables.
  - Individual, or multiple, time series from single or multiple countries.
  - Core and Encouraged Set tables, plus all individual underlying series.
  - Daily Port and Chokepoints data, with charts for metadata and average annual statistics.

### Endpoints

- `obb.economy.available_indicators`
- `obb.economy.indicators`
- `obb.economy.direction_of_trade`
- `obb.economy.shipping.chokepoint_info`
- `obb.economy.shipping.chokepoint_volume`
- `obb.economy.shipping.port_info`
- `obb.economy.shipping.port_volume`
