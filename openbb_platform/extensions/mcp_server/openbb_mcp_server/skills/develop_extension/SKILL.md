---
name: develop_extension
description: This is a complete guide for creating a new OpenBB Platform extension from scratch. Follow every phase in order. When the user says "build me an application that does X", use this guide to scaffold, implement, install, and verify the extension.
---

# Build an OpenBB Platform Extension

This is a complete guide for creating a new OpenBB Platform extension from scratch.
Follow every phase in order. When the user says "build me an application that does X",
use this guide to scaffold, implement, install, and verify the extension.

---

## Phase 1 — Scaffold the Project

The `openbb-cookiecutter` package must be installed in the active Python environment
before scaffolding. Install it with:

```
pip install openbb-cookiecutter
```

Then run the CLI to generate the project skeleton.
All variables have sensible defaults; override only what you need.

### Template Variables

| Variable | Default | Description |
|---|---|---|
| `full_name` | `"Hello World"` | Author name |
| `email` | `"hello@world.com"` | Author email |
| `project_name` | `"OpenBB Python Extension Template"` | Human-readable project name |
| `project_tag` | derived from `project_name` | Hyphenated slug (used as directory name and package identifier) |
| `package_name` | derived from `project_name` | Python package name (lower_snake_case) |
| `provider_name` | derived from `project_name` | Provider identifier (lower_snake_case) |
| `router_name` | derived from `project_name` | Router identifier (lower_snake_case) |
| `obbject_name` | derived from `project_name` | OBBject accessor name (lower_snake_case) |

All derived values are automatically generated from `project_name` — you only need
to supply `project_name` for most cases.

### CLI Command

```
openbb-cookiecutter \
  -o /path/to/output \
  --no-input \
  --extra-context project_name="My Extension Name"
```

Add more `--extra-context KEY=VALUE` pairs to override individual variables.
Use `-f` to overwrite an existing directory.

---

## Phase 2 — Understand the Generated Structure

After scaffolding, you get this tree (with template variables resolved):

```
<project_tag>/
├── pyproject.toml          # Dependencies, entry points (CRITICAL)
├── <package_name>/
│   ├── providers/
│   │   └── <provider_name>/
│   │       ├── __init__.py     # Provider registration (fetcher_dict)
│   │       ├── models/
│   │       │   ├── example.py      # Custom-schema fetcher example
│   │       │   └── ohlc_example.py # Standard-model fetcher example
│   │       └── utils/
│   │           └── helpers.py      # Shared utility functions
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── <router_name>.py        # Router commands (API endpoints)
│   │   ├── <router_name>_views.py  # Chart views (optional)
│   │   └── depends.py              # Dependency injection
│   └── obbject/
│       └── <obbject_name>/
│           └── __init__.py         # OBBject accessors (optional)
└── tests/
    └── conftest.py
```

### The Four Plugin Types

OpenBB discovers extensions via Python entry points in `pyproject.toml`.
Each plugin type has its own entry point group:

| Entry Point Group | What It Registers | Where It Lives |
|---|---|---|
| `openbb_provider_extension` | Data provider (fetchers) | `providers/<name>/__init__.py` |
| `openbb_core_extension` | Router (API endpoints/commands) | `routers/<name>.py` |
| `openbb_charting_extension` | Chart views | `routers/<name>_views.py` |
| `openbb_obbject_extension` | Result post-processing accessors | `obbject/<name>/__init__.py` |

---

## Phase 3 — Implement the Data Provider

This is the core of any extension. A provider fetches data from an external source
and returns it as typed Pydantic models.

### The Three-Class Fetcher Pattern

Every data fetcher follows this structure:

**Class 1 — QueryParams** (input schema):
- Inherits from `openbb_core.provider.abstract.query_params.QueryParams`
- Define all parameters the user can pass (e.g., `symbol`, `start_date`)
- Use `pydantic.Field` for descriptions and defaults

**Class 2 — Data** (output schema):
- Inherits from `openbb_core.provider.abstract.data.Data`
- Define all fields in the response (e.g., `open`, `high`, `low`, `close`, `volume`)
- Use `pydantic.Field` for descriptions
- Use `__alias_dict__` to map source field names to your schema names

**Class 3 — Fetcher** (orchestrator):
- Inherits from `Fetcher[YourQueryParams, list[YourData]]`
- Has exactly three static methods:

  1. `transform_query(params: dict) -> YourQueryParams`
     Pre-process user input. Return a validated QueryParams instance.

  2. `extract_data(query, credentials, **kwargs) -> list[dict]`
     Make the actual HTTP request to the data source. Return raw data as dicts.
     For async fetching, name it `aextract_data` instead.

  3. `transform_data(query, data, **kwargs) -> list[YourData]`
     Convert raw dicts into typed Data model instances.

### Imports for Fetcher Files

```python
from typing import Any
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field
```

### HTTP Requests — Required Utilities

**IMPORTANT:** All HTTP requests inside fetchers and utility helpers **must** use the built-in
utilities from `openbb_core.provider.utils.helpers`. Do **not** create raw
`requests`, `aiohttp`, or `httpx` clients from scratch. The built-in helpers
apply the user's configured HTTP settings (proxy, timeout, user-agent, etc.)
from `system_settings.json` automatically.

#### Building Query Strings

Convert a QueryParams model to a URL query string, optionally excluding
parameters that should not appear in the URL:

```python
from openbb_core.provider.utils.helpers import get_querystring

query_string = get_querystring(query.model_dump(), ["interval", "provider"])
url = f"https://api.example.com/data?{query_string}"
```

`model_dump()` strips `None` values automatically. Pass parameter names to
exclude in the second argument as a list (use `[]` if nothing to exclude).

#### Synchronous Requests

For use inside `extract_data` (sync fetchers):

```python
from openbb_core.provider.utils import make_request

# Returns a requests.Response object
response = make_request(url, headers={"Authorization": f"Bearer {api_key}"})
data = response.json()
```

All `requests.get`/`requests.post` keyword arguments are passed through.

If you need a session object for multiple requests:

```python
from openbb_core.provider.utils.helpers import get_requests_session

session = get_requests_session()
response = session.get(url)
```

#### Asynchronous Requests (Preferred)

For use inside `aextract_data` (async fetchers). **Always prefer async.**

**Single URL** — returns parsed JSON by default:

```python
from openbb_core.provider.utils.helpers import amake_request

data = await amake_request(url)  # returns dict (parsed JSON)
```

**Multiple URLs** — downloads concurrently and returns a list:

```python
from openbb_core.provider.utils.helpers import amake_requests

urls = [f"https://api.example.com/data/{s}" for s in symbols]
all_data = await amake_requests(urls)  # returns list[dict]
```

**Custom response handling (e.g., CSV):** Both `amake_request` and
`amake_requests` default to parsing JSON. For non-JSON content (CSV, text,
binary), pass a `response_callback`:

```python
from io import StringIO
from typing import Any
from pandas import read_csv
from openbb_core.provider.utils.helpers import amake_request

results: list[dict] = []

async def csv_callback(response, _: Any):
    """Parse CSV response into list of dicts."""
    text = await response.text()
    df = read_csv(StringIO(text))
    results.extend(df.to_dict("records"))

await amake_request(url, response_callback=csv_callback)
# results now contains the parsed rows
```

For CSV files with header rows to skip, pass `skiprows` to `read_csv`:

```python
async def csv_callback(response, _: Any):
    text = await response.text()
    df = read_csv(StringIO(text), skiprows=3)
    results.extend(df.to_dict("records"))
```

**Async session object** — if you need a raw `aiohttp.ClientSession`:

```python
from openbb_core.provider.utils.helpers import get_async_requests_session

async with await get_async_requests_session() as session:
    async with session.get(url) as response:
        if response.status != 200:
            raise OpenBBError(f"Failed: {response.status} -> {response.reason}")
        data = await response.json()
```

#### Summary: Which Helper to Use

| Scenario | Function | Module |
|---|---|---|
| Build a query string | `get_querystring()` | `openbb_core.provider.utils.helpers` |
| Sync single request | `make_request()` | `openbb_core.provider.utils` |
| Sync session | `get_requests_session()` | `openbb_core.provider.utils.helpers` |
| Async single request (JSON) | `amake_request()` | `openbb_core.provider.utils.helpers` |
| Async multiple URLs (JSON) | `amake_requests()` | `openbb_core.provider.utils.helpers` |
| Async single/multi (CSV/text) | `amake_request()` + `response_callback` | `openbb_core.provider.utils.helpers` |
| Async raw session | `get_async_requests_session()` | `openbb_core.provider.utils.helpers` |

### Using Standard Models (Multi-Provider Endpoints)

To plug into existing endpoints that other providers already serve (like `EquityHistorical`),
inherit from the standard query/data classes instead of the abstract base classes:

```python
from openbb_core.provider.standard_models.equity_historical import (
    EquityHistoricalData,
    EquityHistoricalQueryParams,
)
```

Then add provider-specific fields as extra attributes.
Use `__alias_dict__` to map the source's field names to the standard field names.

### Registering Fetchers in the Provider

In `providers/<provider_name>/__init__.py`, create a `Provider` instance:

```python
from openbb_core.provider.abstract.provider import Provider

my_provider = Provider(
    name="my_provider",
    description="Description of what this provider does.",
    # credentials=["api_key"],  # Uncomment if an API key is needed
    website="https://example.com",
    fetcher_dict={
        "MyCustomModel": MyCustomFetcher,
        "EquityHistorical": MyEquityHistoricalFetcher,  # Plugs into existing endpoint
    },
)
```

The `fetcher_dict` keys are model names. When a key matches a standard model name
(like `"EquityHistorical"`), this provider becomes selectable via the `provider`
parameter on that existing endpoint.

For custom/new model names, you must also create a router command that references
that model name (see Phase 4).

### Credentials

If your provider needs an API key:
1. Add `credentials=["api_key"]` to the Provider constructor
2. Access it in `extract_data` via `credentials.get("<package_name>_api_key")`
3. Users configure it in their OpenBB user settings

---

## Phase 4 — Implement the Router

The router defines the API endpoints (commands) that users call.

### Router Basics

```python
from openbb_core.app.router import Router

router = Router(prefix="")
```

The top-level prefix is determined by the entry point name in `pyproject.toml`,
not by the `prefix` argument. Only set `prefix` for sub-routers.

### Provider-Backed Command (Standard Pattern)

This is the most common pattern. It connects a router command to one or more
provider fetchers via the model name:

```python
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from pydantic import BaseModel

@router.command(model="MyCustomModel")
async def my_command(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Description of this command."""
    return await OBBject.from_query(Query(**locals()))
```

The four parameters (`cc`, `provider_choices`, `standard_params`, `extra_params`)
and the `OBBject.from_query(Query(**locals()))` return pattern are mandatory and
must be used exactly as shown.

The `model="MyCustomModel"` string must match a key in at least one provider's
`fetcher_dict`.

### Free-Form GET Endpoint

For endpoints that don't use the provider/fetcher system:

```python
@router.command(methods=["GET"])
async def my_endpoint(symbol: str = "AAPL") -> OBBject[dict]:
    """Get some data directly."""
    # Make HTTP requests, compute, etc.
    return OBBject(results={"key": "value"})
```

### Free-Form POST Endpoint

```python
@router.command(methods=["POST"])
async def my_post_endpoint(
    data: BaseModel,   # Body parameters
    flag: bool = False, # Query parameters
) -> OBBject[dict]:
    """Process submitted data."""
    return OBBject(results={"processed": True})
```

### Dependency Injection

Use `routers/depends.py` for shared dependencies:

```python
from typing import Annotated
import requests
from fastapi import Depends
from openbb_core.provider.utils.helpers import get_requests_session

Session = Annotated[requests.Session, Depends(get_requests_session)]
```

Then use `session: Session` as a parameter in your router commands.

### Adding Examples

```python
from openbb_core.app.model.example import APIEx, PythonEx

@router.command(
    model="MyModel",
    examples=[
        PythonEx(
            description="Get data for AAPL",
            code=["obb.my_router.my_command(symbol='AAPL')"],
        )
    ],
)
```

---

## Phase 5 — Entry Points in pyproject.toml

This is **critical** — OpenBB discovers your code entirely through these entry points.

### Provider Entry Point

```toml
[tool.poetry.plugins."openbb_provider_extension"]
my_provider = "my_package.providers.my_provider:my_provider_variable"
```

The variable (`my_provider_variable`) is the `Provider(...)` instance you created
in Phase 3.

### Router Entry Point

```toml
[tool.poetry.plugins."openbb_core_extension"]
my_router = "my_package.routers.my_router:router"
```

The entry point **name** (`my_router`) determines the API path prefix.
For example, `my_router` means endpoints appear under `/my_router/...`.

### Charting Entry Point (Optional)

```toml
[tool.poetry.plugins."openbb_charting_extension"]
my_router = "my_package.routers.my_router_views:MyRouterViews"
```

### OBBject Entry Point (Optional)

```toml
[tool.poetry.plugins."openbb_obbject_extension"]
my_accessor = "my_package.obbject.my_obbject:ext"
my_namespace = "my_package.obbject.my_obbject:class_ext"
```

---

## Phase 6 — Chart Views (Optional)

If you want to add charting support:

```python
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure

class MyRouterViews:
    """Chart views for the router."""

    @staticmethod
    def my_router_my_command(**kwargs) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Create a chart for my_command results."""
        from openbb_charting.core.openbb_figure import OpenBBFigure

        data = kwargs["obbject_item"]
        fig = OpenBBFigure()
        # Build your chart using fig.add_*() methods
        content = fig.show(external=True).to_plotly_json()
        return fig, content
```

Method naming convention: `<router_name>_<command_name>` matching the route path
in lower_snake_case.

---

## Phase 7 — OBBject Accessors (Optional)

Result post-processing extensions that add methods to the `OBBject` response.

### Function Accessor (Property-Like)

```python
from openbb_core.app.model.extension import Extension

ext = Extension(name="to_csv", description="Convert results to CSV string.")

@ext.obbject_accessor
def to_csv(obbject, **kwargs) -> str:
    """Convert to CSV."""
    return obbject.to_dataframe().to_csv()
```

### Class Accessor (Namespaced Methods)

```python
class_ext = Extension(name="my_tools", description="Custom result tools.")

@class_ext.obbject_accessor
class MyTools:
    def __init__(self, obbject):
        self._obbject = obbject

    def summary(self, **kwargs):
        """Return a summary."""
        df = self._obbject.to_dataframe()
        return df.describe()
```

---

## Phase 8 — Install, Build, and Test

### Install in Development Mode

From the generated project root directory:

```
pip install -e ".[dev]"
```

This registers the entry points so OpenBB discovers your extension immediately.

### Build Static Assets with `openbb-build`

**CRITICAL:** After installing a new extension, or after making changes to any
of the following, you **must** run `openbb-build` before using the Python
interface (`obb.<router>.<command>(...)`):

- **Model definitions** — `QueryParams` or `Data` classes (field names, types,
  defaults, descriptions)
- **Provider registration** — changes to `fetcher_dict` keys, adding/removing
  fetchers
- **Router commands** — adding, removing, or renaming `@router.command()`
  endpoints
- **Entry points** — changes to `pyproject.toml` plugin entries
- **Any importable item in the registration chain** — the `Provider(...)`
  instance, router module, or model module paths

You do **not** need to re-run `openbb-build` when changing:

- Logic inside `extract_data` / `aextract_data` / `transform_data` /
  `transform_query` static methods (the Fetcher method bodies)
- Utility/helper functions
- Internal implementation details that don't affect the public schema

```
openbb-build
```

This regenerates the static assets (type stubs, package interface, provider
maps) that the Python interface relies on. Without this step, new or modified
commands will not appear on the `obb` object and calls will fail.

**When running as an API server** (e.g., via `uvicorn` or the MCP server),
static assets are **not used** — the API discovers extensions dynamically at
startup. You do not need to run `openbb-build` for API-only usage.

### Verify Installation

Start a Python session and check:

```python
from openbb import obb
# Your new commands should appear:
# obb.<router_name>.<command_name>(...)
```

Or start the API server and verify the new endpoints appear.

### Run Tests

```
pytest tests/ -v
```

The generated `tests/conftest.py` sets `OPENBB_AUTO_BUILD=true` for proper
test environment setup.

---

## Workflow Summary

When a user asks "Build me an application that does X":

1. **Analyze** — Determine what data sources are needed, what endpoints to expose,
   and whether to use standard models or custom schemas.
2. **Scaffold** — Run `openbb-cookiecutter` with a meaningful `project_name`.
3. **Delete examples** — Remove `example.py` and `ohlc_example.py` from the models
   directory. Clean up the example router commands.
4. **Implement models** — Create `QueryParams` + `Data` + `Fetcher` classes for each
   data source in `providers/<name>/models/`.
5. **Register fetchers** — Update `providers/<name>/__init__.py` with the `fetcher_dict`.
6. **Implement router** — Create `@router.command(model="...")` endpoints in
   `routers/<name>.py`.
7. **Update entry points** — Ensure `pyproject.toml` entry points match your actual
   module paths and variable names.
8. **Add dependencies** — Add any third-party packages to `[tool.poetry.dependencies]`
   in `pyproject.toml`.
9. **Install** — Run `pip install -e ".[dev]"` from the project root.
10. **Build** — Run `openbb-build` to regenerate static assets for the Python
    interface. Skip this step if only using the API server.
11. **Test** — Verify the commands work, then write tests.
