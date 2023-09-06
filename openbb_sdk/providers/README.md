# Providers

## Supported Providers

All currently supported providers are listed below.

| Provider | URL |
| --- | --- |
| [FMP](./fmp/README.md) | https://financialmodelingprep.com/ |
| [Polygon](./polygon/README.md) | https://polygon.io/ |
| [Benzinga](./benzinga/README.md) | https://www.benzinga.com/ |
| [FRED](./fred/README.md) | https://fred.stlouisfed.org/ |

## Default Provider Configuration

To configure the default providers for each route, edit the `.openbb_sdk/user_settings.json` file in your home directory using the following template:

```json
{
    "defaults": {
        "routes": {
            "/stocks/load": {
                "provider": "fmp"
            },
            "/stocks/fa/balance": {
                "provider": "polygon"
            },
            ...
        }
    }
}
```

## Provider Information

Every provider is located within a directory, with the following structure:

```{.bash}
openbb_sdk
└───providers
    └───<provider_name>
        |   README.md
        │   pyproject.toml
        │   poetry.lock
        |───tests
        └───openbb_<provider_name>
            │   __init__.py
            |───models
            |   |───<some model>.py
            |   └───...
            └───utils
                |───<some helper>.py
                └───...
```

The models define the data structures that are used to query the provider endpoints and store the response data.
