# Government of Canada Provider Extension

This package provides access to Canadian government and central-bank data, integrating
the Bank of Canada Valet API and the Statistics Canada SDMX REST API.

## Installation

Install into a Python environment (3.10 - 3.13) from PyPI with:

```sh
pip install openbb-government-ca
```

Then build the Python static assets:

```sh
openbb-build
```

## Credentials

Credentials are not required. Both the Bank of Canada and Statistics Canada APIs are public.

## Coverage

Coverage is added incrementally. See the package namespaces:

- `obb.boc.*` — Bank of Canada data
- `obb.statscan.*` — Statistics Canada data

## Usage

The package can be used as a Python module, or a REST API.

### REST API

Start the server over localhost with:

```sh
openbb-api
```

### Python

```python
from openbb import obb
```
