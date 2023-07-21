# Table of contents

- [Table of contents](#table-of-contents)
- [OpenBB SDK](#openbb-sdk)
  - [Pre-requisites](#pre-requisites)
  - [Installation](#installation)
  - [API keys](#api-keys)
    - [From local file](#from-local-file)
    - [From runtime](#from-runtime)
    - [From OpenBB Hub](#from-openbb-hub)
  - [Python Usage](#python-usage)
  - [API Usage](#api-usage)
  - [Docker](#docker)
  - [Development](#development)

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
pip install ./openbb_sdk
```

This will install the SDK and all the dependencies into the site-packages folder of the virtual environment.

While we're still developing it is required to create the static python interface:

```python
import openbb
openbb._rebuild_python_interface()
exit()
```

Right now you need to do this before the first launch and every time you install or uninstall a new extension.

## API keys

To connect to APIs you need to provide the API keys. Here 3 options how you can provide them:

1. From local file
2. At runtime
3. From OpenBB Hub

### From local file

You can specify the keys from the `~/.openbb_sdk/user_settings.json` file.

Create this file with the following template:

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

### From runtime

You can also specify the keys at runtime:

```python
from openbb import obb
obb.settings.credentials.fmp_api_key = "REPLACE_ME"
obb.settings.credentials.polygon_api_key = "REPLACE_ME"
```

### From OpenBB Hub

You can also load your the keys from the OpenBB Hub.

```python
from openbb import obb
openbb.account.login(username="REPLACE_ME", password="REPLACE_ME")
```

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

Navigate to <http://0.0.0.0:8000/docs> to see the swagger API documentation.

Authorize with the developer credentials: openbb/openbb

## Docker

You can use the API through docker.

To build the image from the repo root run:

```bash
docker build -f build/docker/api.dockerfile -t openbb-sdk:latest .
```

To run the image:

```bash
docker run --rm -p8000:8000 -v ~/.openbb_sdk:/root/.openbb_sdk openbb-sdk:latest
```

This will mount the local `~/.openbb_sdk` folder into the docker container so you can use the API keys from there and it will expose the API on port 8000.

## Development

From the root of the OpenBB Terminal repo run:

`poetry install -C ./openbb_sdk`

When developing a specific extension cd into the extension folder and run:

`pip install -U -e .`
