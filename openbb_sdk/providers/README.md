# Providers

## Supported Providers

All currently supported providers are listed below.

| Provider |
| --- |
| [FMP](./fmp/README.md) |
| [Polygon](./polygon/README.md) |
| [Benzinga](./benzinga/README.md) |
| [FRED](./fred/README.md) |

## Default Provider Configuration

To configure the default providers for each route, edit the `.openbb_sdk/user_settings.json` file in your home directory by adding the `defaults` section, a `routes` subsection and for every route, the default provider desired. A sample is shown below.

```json
{
    "defaults": {
        "routes": {
            "/stocks/fa/balance": {
                "provider": "polygon"
            },
            "/stocks/load": {
                "provider": "fmp"
            },
            "/stocks/news": {
                "provider": "benzinga"
            }
        }
    }
}
```

## Provider Information

Every provider is located within a folder, with the following structure:

```{.bash}
openbb_sdk
└───providers
    └───<provider_name>
        |   README.md
        │   `pyproject.toml`
        │   `poetry.lock`
        └───openbb_<provider_name>
            │   `init.py`
            │   <some functionality>.py
            │   ...
```

The `openbb_<provider_name>` folder contains the provider's source code. The `README.md` file contains the provider's documentation. The `pyproject.toml` and `poetry.lock` files contain the provider's dependencies.
