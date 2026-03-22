---
name: build_workspace_app
description: This guide covers the full lifecycle of building, running, and serving a custom OpenBB Workspace application from an extension project scaffolded by `openbb-cookiecutter`. It assumes the project shell already exists (see the `develop_extension` skill for scaffolding instructions).
---

# Build and Run OpenBB Workspace Applications

This guide covers the full lifecycle of building, running, and serving a custom
OpenBB Workspace application from an extension project scaffolded by
`openbb-cookiecutter`. It assumes the project shell already exists
(see the `develop_extension` skill for scaffolding instructions).

---

## Prerequisites

Ensure the following packages are installed in the active Python environment:

```
pip install openbb-core openbb-platform-api openbb-devtools
```

- `openbb-core` provides the Router, Provider, OBBject, and Fetcher base classes.
- `openbb-platform-api` provides the `openbb-api` CLI for serving backends
  and auto-generating `widgets.json` for OpenBB Workspace.
- `openbb-devtools` provides `pytest`, cassette recording, and QA utilities.

If you also need the Python Interface wrapper (the `obb` object), install the
main package:

```
pip install openbb --no-deps
```

---

## Architecture Overview

OpenBB is built on FastAPI and Pydantic. The application has two independent
interfaces that share core logic and models:

- **Python Interface** — wraps installed routers into an `obb` Python package
  with auto-generated docstrings and function signatures. Requires a build step
  (`openbb-build`) to generate static assets.
- **REST API** — a FastAPI instance with all installed routers available via
  HTTP. Import it with `from openbb_core.api.rest_api import app` or launch
  with `uvicorn openbb_core.api.rest_api:app`.

The application is the product of all installed extensions. With just `openbb-core`
there are no routers or endpoints — users compose their own combinations.

### Key Classes

| Class | Import | Purpose |
|---|---|---|
| `Router` | `openbb_core.app.router` | Subclass of `fastapi.APIRouter`; defines commands |
| `OBBject` | `openbb_core.app.model.obbject` | Standard response object with results, provider, warnings, extra |
| `Provider` | `openbb_core.provider.abstract.provider` | Registers fetchers for the provider interface |
| `Fetcher` | `openbb_core.provider.abstract.fetcher` | TET pipeline: Transform query → Extract data → Transform data |
| `QueryParams` | `openbb_core.provider.abstract.query_params` | Base class for input parameters |
| `Data` | `openbb_core.provider.abstract.data` | Base class for output data schemas |

---

## Router Extensions (API Endpoints)

Router extensions are the user-facing endpoints that power the REST API, MCP,
and Python Interface.

### Creating a Router

```python
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router

router = Router(prefix="", description="My custom extension.")
```

The top-level API path prefix is determined by the entry point name in
`pyproject.toml`, not the `prefix` argument. Only use `prefix` for sub-routers.

```toml
[tool.poetry.plugins."openbb_core_extension"]
my_app = "my_package.routers.my_router:router"
```

Commands appear at `/my_app/...` in the API and `obb.my_app.` in Python.

### Provider Interface Endpoints

Connect a router command to one or more provider fetchers via the model name:

```python
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import ExtraParams, ProviderChoices, StandardParams
from openbb_core.app.query import Query
from pydantic import BaseModel

@router.command(model="MyModel")
async def my_command(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> OBBject[BaseModel]:
    """Description of this command."""
    return await OBBject.from_query(Query(**locals()))
```

The four parameters and the `OBBject.from_query(Query(**locals()))` return are
mandatory and must be used exactly as shown.

### Basic GET Endpoint

```python
@router.command(methods=["GET"])
async def hello() -> OBBject[str]:
    """OpenBB Hello World."""
    return OBBject(results="Hello from the extension!")
```

### Basic POST Endpoint

```python
from openbb_core.provider.abstract.data import Data

@router.command(methods=["POST"])
async def process(data: Data, some_param: str) -> OBBject:
    """Process submitted data."""
    return OBBject(results=data.model_dump())
```

### Decorator Parameters

`@router.command` accepts:
- `model` — metamodel name linking to Provider fetchers
- `methods` — list of HTTP methods, typically `["GET"]` or `["POST"]`
- `examples` — list of `APIEx` or `PythonEx` for docs
- `deprecated` — deprecation notice
- `exclude_from_api` — Python Interface only
- `no_validate` — skip response validation, treat output as `Any`
- `openapi_extra` — dictionary for inline `widget_config` or `mcp_config`

### Using FastAPI APIRouter Directly

Access the underlying FastAPI router via `router._api_router`:

```python
@router._api_router.get("/also_empty")
async def also_empty(param: str) -> str:
    """Also empty."""
    return "Hello world!"
```

---

## From FastAPI — Converting Existing Apps

Any existing FastAPI application can become an OpenBB extension without changing
code. Define the entry point in `pyproject.toml` pointed at the FastAPI or
APIRouter instance:

```toml
[tool.poetry.plugins."openbb_core_extension"]
my_app = "my_package.app:app"
```

Install the package and build static assets:

```
pip install -e .
openbb-build
```

Known limitations:
- Authorization hooks are not injected into the Python Interface
- Request-bound dependencies or those returning None are not injected
- WebSockets are not supported in the Python Interface
- Multi-method routes (GET + POST on same path) may not generate correctly

---

## Serving with openbb-api (Workspace Backends)

The `openbb-api` CLI converts a FastAPI instance into an OpenBB Workspace
backend with auto-generated widget definitions.

### Basic Usage

```
# Start with default OpenBB extensions
openbb-api

# Start with a custom FastAPI file
openbb-api --app ./my_app.py --host 0.0.0.0 --port 8005

# Factory function pattern
openbb-api --app my_app.py:create_app --factory

# Custom FastAPI instance name
openbb-api --app my_app.py --name my_app
```

Defaults are `--host 127.0.0.1 --port 6900`, falling back to the next
available port if already in use.

### Key Arguments

| Argument | Description |
|---|---|
| `--app` | Path to Python file with a FastAPI instance |
| `--name` | Name of the FastAPI instance (default: `app`) |
| `--factory` | Flag if the app name is a factory function |
| `--editable` | Make `widgets.json` editable at runtime |
| `--no-build` | Load existing `widgets.json` without checking for updates |
| `--exclude` | JSON list of API paths to exclude from widgets |
| `--widgets-json` | Custom path for `widgets.json` |
| `--apps-json` | Custom path for `workspace_apps.json` |

All remaining arguments are passed to `uvicorn.run`.

---

## Inline Widget Definitions

Widget properties can be defined inline in your code via `openapi_extra`:

```python
@app.get(
    "/some_endpoint",
    openapi_extra={
        "widget_config": {
            "name": "Custom Widget Name",
            "description": "Override docstring description",
        }
    },
)
async def some_endpoint():
    """Description from docstring."""
    pass
```

### Exclude an Endpoint from Widgets

```python
@app.get(
    "/internal_endpoint",
    openapi_extra={"widget_config": {"exclude": True}},
)
async def internal_endpoint():
    return [{"label": "Choice 1", "value": "choice1"}]
```

### Dropdown Parameters

Dropdowns are auto-generated from `Literal` types:

```python
from typing import Literal

@app.get("/with_dropdown")
async def with_dropdown(
    choices: Literal["Choice 1", "Choice 2", "Choice 3"] = "Choice 3"
):
    pass
```

### Column Definitions for Tables

Use Pydantic response models to auto-generate table column definitions:

```python
import datetime
from pydantic import BaseModel, Field

class MyData(BaseModel):
    date: datetime.date = Field(description="The date.")
    value: float = Field(description="The value.")

@app.get("/my_data")
async def my_data() -> list[MyData]:
    """Widget with typed columns."""
    return [MyData(date=datetime.date.today(), value=42.0)]
```

### Widget Types by Return Type

| Return Type | Widget Type |
|---|---|
| `list[dict]` or `list[BaseModel]` | Table (AgGrid) |
| `str` | Markdown |
| `dict` (with `widget_config.type="chart"`) | Plotly Chart |
| `MetricResponseModel` | Metric |
| `PdfResponseModel` | PDF |

### Response Models for Special Widgets

```python
from openbb_platform_api.response_models import MetricResponseModel, PdfResponseModel

@app.get("/metric", response_model=MetricResponseModel)
async def metric():
    """A metric widget."""
    return dict(label="Revenue", value=12345, delta=5.67)

@app.get("/pdf", response_model=PdfResponseModel)
async def open_pdf(file_path: str):
    """Open a PDF document."""
    with open(file_path, "rb") as f:
        return dict(content=f.read())
```

### Plotly Chart Widget

```python
@app.get(
    "/chart",
    openapi_extra={"widget_config": {"type": "chart"}},
)
async def chart() -> dict:
    """A chart widget."""
    from plotly.graph_objs import Bar, Layout, Figure

    fig = Figure(
        data=[Bar(x=["A", "B", "C"], y=[1, 2, 3])],
        layout=Layout(title="My Chart", template="plotly_dark"),
    )
    return fig.to_plotly_json()
```

### JSON Schema Extra for Parameters

Annotate parameters with additional widget configuration:

```python
from typing import Annotated
from fastapi import Query

my_param: Annotated[
    str,
    Query(
        title="My Title",
        description="Detailed hover text",
        json_schema_extra={
            "x-widget_config": {
                "optionsEndpoint": "/my_choices_endpoint"
            }
        },
    ),
]
```

### Form Input Widget

Create an input form tied to a table:
- GET endpoint defines `widget_config.form_endpoint` pointing to the POST route
- POST route accepts a single Pydantic model argument

---

## OBBject Extensions (Result Post-Processing)

Extend the `OBBject` response with custom methods, accessible in the Python Interface.

### Class Accessor (Namespaced Methods)

```python
from openbb_core.app.model.extension import Extension

ext = Extension(name="my_tools", description="Custom result tools.")

@ext.obbject_accessor
class MyTools:
    def __init__(self, obbject):
        self._obbject = obbject

    def summary(self):
        """Return a summary."""
        return self._obbject.to_dataframe().describe()
```

Register in `pyproject.toml`:

```toml
[tool.poetry.plugins."openbb_obbject_extension"]
my_tools = "my_package.obbject.my_ext:ext"
```

### Callable Accessor (Property-Like)

```python
ext = Extension(name="to_csv", description="Convert results to CSV.")

@ext.obbject_accessor
def to_csv(obbject):
    """Convert to CSV string."""
    return obbject.to_dataframe().to_csv()
```

### OBBject Output Conversion Methods

Every `OBBject` has built-in conversion methods:
- `to_df()` / `to_dataframe()` — Pandas DataFrame
- `to_dict(orientation=...)` — Python dict
- `to_numpy()` — NumPy array
- `to_polars()` — Polars DataFrame (requires `polars` installed)
- `model_dump()` — Complete object as dict
- `model_dump_json()` — Serialized JSON string

---

## OBBject Plugins (Pre-Return Interceptors)

Plugins execute before the response is returned, compatible with both REST API
and Python Interface. They can conditionally alter the output of any command.

**WARNING**: Plugins are considered potentially dangerous. The environment must
be explicitly configured to allow them.

In `system_settings.json`:

```json
{
    "allow_on_command_output": true,
    "allow_mutable_extensions": true
}
```

### Plugin Configuration

```python
from openbb_core.app.model.extension import Extension

plugin = Extension(
    name="my_plugin",
    description="Intercept output before return.",
    on_command_output=True,
    command_output_paths=["/my_router/my_command"],
    immutable=False,
    results_only=False,
)
```

Key parameters:
- `on_command_output=True` — required for plugins
- `command_output_paths` — list of endpoint paths to intercept (None = all)
- `immutable=False` — set to allow modifying the response object
- `results_only=True` — receive only the `results` portion instead of full OBBject

### Plugin Code

```python
@plugin.obbject_accessor
def my_plugin_func(obbject):
    """Modify or inspect the response before it returns."""
    # Modify obbject directly; do NOT return anything
    pass
```

---

## Charting Extensions (Views)

Add custom chart views to any router endpoint, activated when the user sets
`chart=True`.

### Structure

```python
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure

class MyViews:
    """Chart views for the router."""

    @staticmethod
    def my_router_my_command(**kwargs) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Chart for my_command."""
        from openbb_charting.core.openbb_figure import OpenBBFigure

        data = kwargs["obbject_item"]
        fig = OpenBBFigure()
        # Build chart with fig.add_*() methods
        content = fig.show(external=True).to_plotly_json()
        return fig, content
```

Method naming convention: `<router_name>_<command_name>` matching the route path
in lower_snake_case.

Register in `pyproject.toml`:

```toml
[tool.poetry.plugins."openbb_charting_extension"]
my_router = "my_package.routers.my_views:MyViews"
```

### Kwargs Available in Views

| Key | Content |
|---|---|
| `obbject_item` | Validated results object |
| `charting_settings` | User charting preferences |
| `standard_params` | Standard model parameters |
| `extra_params` | Provider-specific parameters |
| `provider` | Provider name used |
| `extra` | Execution metadata |

---

## HTTP Requests in Fetchers

Use the built-in utilities instead of creating new clients from scratch.

### Query String Helper

```python
from openbb_core.provider.utils.helpers import get_querystring

query_string = get_querystring(query.model_dump(), ["exclude_this_param"])
```

### Synchronous Requests

```python
from openbb_core.provider.utils import make_request

response = make_request(url, headers=headers, params=params)
```

### Requests Session

```python
from openbb_core.provider.utils.helpers import get_requests_session

session = get_requests_session()
```

### Asynchronous Requests (AIOHTTP)

```python
from openbb_core.provider.utils.helpers import amake_request

response_json = await amake_request(url)
```

### Multi-URL Async Requests

```python
from openbb_core.provider.utils.helpers import amake_requests

results = await amake_requests([url1, url2, url3])
```

### Custom Response Callback

```python
from io import StringIO
from pandas import DataFrame

results = []

async def response_callback(response, _):
    text = await response.text()
    data = DataFrame(StringIO(text), skiprows=2)
    results.append(data.to_dict("records"))

await amake_requests(url, response_callback=response_callback)
```

### Async Session

```python
from openbb_core.provider.utils.helpers import get_async_requests_session

async with await get_async_requests_session() as session:
    async with await session.get(url) as response:
        data = await response.json()
```

### Async Fetchers

Use `aextract_data` instead of `extract_data` for async fetchers:

```python
@staticmethod
async def aextract_data(
    query: MyQueryParams,
    credentials: dict[str, str] | None,
    **kwargs: Any,
) -> list[dict]:
    """Async data extraction."""
    ...
```

---

## Testing

### Built-In Fetcher Test

Every Fetcher has a `.test()` method for quick validation:

```python
from my_package.providers.my_provider.models.my_model import MyFetcher

fetcher = MyFetcher()
fetcher.test({"symbol": "AAPL"}, {})  # Returns None on success
```

### Unit Tests with Cassettes

Install dev tools and use `pytest_recorder` for HTTP cassette recording:

```
pip install openbb-devtools
pytest test_my_fetcher.py --record http
```

Subsequent test runs replay the recorded HTTP interactions.

### Running Tests

```
# Unit tests only
pytest tests/ -m "not integration"

# Integration tests only
pytest tests/ -m integration

# All tests
pytest tests/
```

### Integration Testing

For API integration tests, start a local server first:

```
uvicorn openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 --reload
```

---

## Install and Build

### Development Install

From the project root:

```
pip install -e ".[dev]"
```

### Build Python Interface

After installing or removing extensions, regenerate static assets:

```
openbb-build
```

### Verify in Python

```python
from openbb import obb
# Your commands appear under obb.<router_name>.<command_name>()
```

### Serve as Workspace Backend

```
openbb-api --app ./my_app.py --editable --host 0.0.0.0 --port 6900
```

---

## Workflow Summary

When a user asks "Build me a Workspace application that does X":

1. **Scaffold** the project with `openbb-cookiecutter` (see `develop_extension` skill).
2. **Remove** example files and clean up boilerplate.
3. **Implement fetchers** for each data source in `providers/<name>/models/`.
4. **Register fetchers** in `providers/<name>/__init__.py` via `fetcher_dict`.
5. **Implement router commands** in `routers/<name>.py`.
6. **Add widget config** via `openapi_extra` for Workspace-specific behavior.
7. **Update `pyproject.toml`** entry points and dependencies.
8. **Install** with `pip install -e ".[dev]"`.
9. **Build** static assets with `openbb-build`.
10. **Serve** with `openbb-api` and verify widgets in OpenBB Workspace.
11. **Test** with `pytest` and fetcher `.test()` methods.
