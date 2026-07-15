# OpenBB NSE Provider

This extension integrates data from the [National Stock Exchange of India (NSE)](https://www.nseindia.com) into the OpenBB Platform.

Index data is sourced from the official constituent files published by **NSE Indices Limited** (`niftyindices.com`). These are statically published files, so **no API key is required** and there is no dependency on the anti-bot `nseindia.com` quote API.

## Installation

```bash
pip install openbb-nse
```

Documentation is available [here](https://docs.openbb.co/platform).

## Coverage

| Command | Standard model | Source |
| --- | --- | --- |
| `obb.index.constituents` | `IndexConstituents` | NSE Indices official constituent files |

## Usage

```python
from openbb import obb

# Constituents of the NIFTY 500
obb.index.constituents("nifty_500", provider="nse")

# Bank Nifty
obb.index.constituents("nifty_bank", provider="nse")
```

### Supported indices

`nifty_50`, `nifty_100`, `nifty_200`, `nifty_500`, `nifty_next_50`, `nifty_bank`,
`nifty_it`, `nifty_auto`, `nifty_pharma`, `nifty_fmcg`, `nifty_metal`, `nifty_energy`,
`nifty_fin_service`, `nifty_midcap_100`, `nifty_smallcap_100`.

In addition to the standard `symbol` and `name` fields, this provider enriches each
constituent with the India-native `industry`, `isin`, and `series` fields.
