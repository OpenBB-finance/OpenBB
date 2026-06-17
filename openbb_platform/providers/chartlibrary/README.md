# OpenBB ChartLibrary Provider

This extension integrates ChartLibrary pattern similarity search into the
OpenBB Platform.

The provider calls ChartLibrary's documented `POST /api/v1/search/text` endpoint
with bearer-token authentication and exposes the results through:

```python
obb.technical.pattern_similarity(
    symbol="NVDA",
    date="2025-01-15",
    timeframe="rth",
    provider="chartlibrary",
)
```

Set the credential as `chartlibrary_api_key` in OpenBB user settings.

## Installation

To install the extension, run the following command in this folder:

```bash
pip install openbb-chartlibrary
```

Documentation available [here](https://docs.openbb.co/platform/developer_guide/contributing).
