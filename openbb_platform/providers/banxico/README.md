# OpenBB Banxico Provider

This extension integrates data from the Banco de México (Banxico) Economic
Information System (SIE) into the OpenBB Platform.

## Supported data

The first release provides historical USD/MXN FIX exchange-rate observations
from Banxico series `SF43718`. The provider currently accepts the symbols
`USDMXN` and `USD-MXN`.

## Installation

Install the provider with pip:

```bash
pip install openbb-banxico
```

For local development, install the package from this directory in editable
mode:

```bash
pip install -e openbb_platform/providers/banxico
```

## Credentials

Banxico requires an SIE API token. Request one from the [Banxico SIE token
page](https://www.banxico.org.mx/SieAPIRest/service/v1/token), then save it
through OpenBB's local credential settings as `banxico_api_key`. The token is
passed to Banxico in the `Bmx-Token` request header.

Never place the token in source code, tests, HTTP cassettes, or Git commits.

## Example

After installing OpenBB and this provider, query the historical series with:

```python
from openbb import obb

result = obb.currency.price.historical(
    symbol="USDMXN",
    start_date="2024-01-02",
    end_date="2024-01-05",
    provider="banxico",
)
```
