# OpenBB SDK

## Pre-requisites

To install and use you need:

- A fresh virtual environment
- Python 3.8 or higher
- API keys for the APIs you want to use

To develop you need:

- Poetry 1.5.1 or higher
- ruff 0.0.256
- mypy 1.4.1
- black

## Installation

To install the SDK in the virtual environment from the repo root run:

```bash
pip install ./openbb-sdk
```

This will install the SDK and all the dependencies into the site-packages folder of the virtual environment.

When working with the source code of the SDK it is required to create the static python interface:

```python
import openbb
openbb._rebuild_python_interface()
exit()
```

## API keys

To connect to APIs you need to provide the API keys.

When developing locally you can specify your keys in the `~/.openbb_sdk/user_settings.json`.

Create this file with the following contents:

```json
{
  "credentials": {
    "fmp_api_key": "REPLACE_ME",
    "polygon_api_key": "REPLACE_ME",
    "benzinga_api_key": "REPLACE_ME",
    "fred_api_key": "REPLACE_ME"
  }
}
```

Then add your API keys there and it should work.

## Python Usage

Import and basic usage:

 ```python
 from openbb import obb
 aapl = obb.stocks.load(symbol="AAPL", start_date="2020-01-01", provider="fmp")
 df = aapl.to_dataframe()
 df.head()
 ```

## API Usage

Launch the API with:

```bash
uvicorn openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 --reload
```

Navigate to http://0.0.0.0:8000/docs to see the swagger API documentation.

Authorize with the developer credentials: openbb/openbb

## Development

From the root of the OpenBB Terminal repo run:

`poetry install -C ./openbb_sdk`

When developing a specific extension cd into the extension folder and run:

`poetry install`
