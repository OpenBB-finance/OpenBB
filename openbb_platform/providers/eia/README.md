# OpenBB EIA Provider Extension

This module integrates the [EIA](https://eia.gov) data provider into the OpenBB Platform.

## Installation

### PyPI

```sh
pip install openbb-eia
```

### From Source

After cloning the main repository, navigate into this folder and enter:

```sh
pip install .
```

To install in editable mode:

```sh
pip install -e .
```

## Coverage

### Weekly Petroluem Status Report

The WPSR is comprised of thirteen (excludes discontinued series) high-level categories with each containing a subset of tables. Data is from the static Excel files published [here](https://www.eia.gov/petroleum/supply/weekly/), and each file represents a single category.

All data from a single category is returned by supplying "all" to the `table` parameter of the WPSR endpoint.

Tables from the WPSR are returned in a flat format in the same order as presented in the Excel files. The response is suitable for pivot tables and SQL storage.

### Endpoints

- `obb.commodity.petroleum_status_report`

## Authorization

**Note**: This section is for future expansion.

Functions calling the EIA's API require free registration and an API key, obtained [here](https://www.eia.gov/opendata/register.php).

Authorization can be made via:

### OpenBB Hub

Add the key as "eia_api_key" in the OpenBB Hub Credentials page, [here](https://my.openbb.co/app/platform/credentials)

### `user_settings.json`

Add it to the credentials section of `~/.openbb_platform/user_settings.json`

```json
{
    "credentials": {
        "eia_api_key": "REPLACE_WITH_YOUR_KEY"
    }
}
```

### Current Python Session

The credential can be added for the current session only, after import the OpenBB paackage.

```python
from openbb import obb

obb.user.credentials.eia_api_key = "REPLACE_WITH_YOUR_KEY"
```
