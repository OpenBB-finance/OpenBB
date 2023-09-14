# Table of contents

- [Table of contents](#table-of-contents)
  - [Pre-requisites](#pre-requisites)
  - [Installation](#installation)
  - [API keys](#api-keys)
    - [1. From local file](#1-from-local-file)
    - [2. From runtime](#2-from-runtime)
    - [3. From OpenBB Hub](#3-from-openbb-hub)
  - [Python Usage](#python-usage)
  - [API Usage](#api-usage)
  - [Docker](#docker)
  - [Development](#development)
    - [Import time](#import-time)

## Pre-requisites

To install and use the SDK you need:

- A fresh virtual environment
- Python 3.8 or higher
- API keys for the APIs you want to use

For development you need:

- Poetry 1.5.1 or higher
- ruff 0.0.256
- mypy 1.4.1
- black

## Installation

To install the SDK in a virtual environment from the repo root run:

```bash
pip install ./openbb_sdk
```

This will install the SDK and all its dependencies into the site-packages directory of the virtual environment.

## API keys

To use your API keys you need to configure them. Here are the 3 options on how to do it:

1. From local file
2. At runtime
3. From OpenBB Hub

### 1. From local file

You can specify the keys in the `~/.openbb_sdk/user_settings.json` file.

Create this file using the following template and replace the values with your keys:

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

### 2. From runtime

You can also specify your keys at runtime:

```python
from openbb import obb
obb.user.credentials.fmp_api_key = "REPLACE_ME"
obb.user.credentials.polygon_api_key = "REPLACE_ME"
```

### 3. From OpenBB Hub

You can also load your the keys from the OpenBB Hub.

```python
from openbb import obb
openbb.account.login(username="REPLACE_ME", password="REPLACE_ME")
```

## Python usage

Import and basic usage:

```python
from openbb import obb
aapl = obb.stocks.load("AAPL")
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

You can use the API through Docker.

To build the image, from the repo root run:

```bash
docker build -f build/docker/api.dockerfile -t openbb-sdk:latest .
```

To run this newly-built image:

```bash
docker run --rm -p8000:8000 -v ~/.openbb_sdk:/root/.openbb_sdk openbb-sdk:latest
```

This will mount the local `~/.openbb_sdk` directory into the Docker container so you can use the API keys from there and it will expose the API on port `8000`.

## Development

From the root of the OpenBB Terminal repo, run:

`poetry install -C ./openbb_sdk`

When developing a specific extension `cd` into the extension directory and run:

`pip install -U -e .`

While we're still developing, it is often required to reinstall extensions:

```python
python -c "import openbb; openbb.build()"
```

You need to do this every time you install or uninstall a new extension or to reinstall all extensions.

### Import time

We aim to have a short import time. To measure that we use `tuna`.

- https://pypi.org/project/tuna/

To visualize the import time breakdown by module, run the following commands from `openbb_sdk` directory:

```bash
pip install tuna
python -X importtime openbb/__init__.py 2> import.log
tuna import.log
```
