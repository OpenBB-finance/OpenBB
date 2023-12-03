# Providers

## Available Providers

See full list of available providers in the [PROVIDERS file](../PROVIDERS.md)

## Default Provider Configuration

To configure the default providers for each route, edit the `.openbb_platform/user_settings.json` file in your home directory using the following template:

```json
{
    "defaults": {
        "routes": {
            "/equity/price/historical": {
                "provider": "fmp"
            },
            "/equity/fundamental/balance": {
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
openbb_platform
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

See [CONTRIBUTING file](../CONTRIBUTING.md) for more details
