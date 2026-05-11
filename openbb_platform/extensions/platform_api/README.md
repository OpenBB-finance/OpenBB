# OpenBB Platform API

Launcher and widgets builder for the OpenBB Workspace [custom backend](https://docs.openbb.co/workspace/data-integration). Wraps any FastAPI application with the metadata, exception handling, and `widgets.json` generation that OpenBB Workspace expects — so a regular FastAPI app becomes a Workspace data source with no glue code.

> **Full documentation:** [docs.openbb.co/odp/python/extensions/interface/openbb-api](https://docs.openbb.co/odp/python/extensions/interface/openbb-api)

## Install

```sh
pip install openbb-platform-api
```

Python ≥ 3.10. Already included when you install [`openbb`](https://docs.openbb.co/platform/installation).

## Quick start

```sh
# Launch the bundled OpenBB Platform on http://127.0.0.1:6900
openbb-api

# Launch your own FastAPI app
openbb-api --app /path/to/your_app.py

# Factory function?
openbb-api --app some_file.py:create_app --factory

# Launch as a proxy from an openbb-cli .spec file
openbb-api --spec /path/to/cli.spec
```

`widgets.json` is auto-generated from your routes' types, response models, and docstrings. Plotly returns become chart widgets, `BaseModel` returns become tables, scalars become metrics — no manual wiring.

## Spec-driven proxy mode

Generate a spec file with `openbb-cli` against any OpenBB Platform deployment, then launch a Workspace-compatible backend that proxies every command to that upstream:

```sh
# Generate the spec once
openbb --generate-spec --server https://api.example.com -o cli.spec

# Launch the proxy
openbb-api --spec cli.spec
```

Each command in the spec becomes a FastAPI route at its `url_path`; the launcher forwards every request to the spec's `base_url` (preserving query, body, and non-hop-by-hop headers). `widgets.json` is generated from the spec's parameter and response-schema metadata via the same builder used for in-process apps.

Useful for shipping a thin frontend container that talks to a managed backend in another cluster, without bundling `openbb-core` or any provider extensions. `--spec` is mutually exclusive with `--app`.

### `[spec]` config — credentials and base-URL override

A `[spec]` table in `openbb.toml` carries the path plus the bits the file alone can't provide — `base_url` overrides for staging/prod, and `headers` injected on every upstream request. Header values support the same `$VAR` substitution as `[env]`, so credentials live in environment variables (or `[env]` entries that read from them) and the TOML just maps them onto upstream header names:

```toml
[env]
OPENBB_UPSTREAM_TOKEN = "$GITHUB_TOKEN"   # or any orchestrator-injected secret

[spec]
path     = "/etc/openbb/cli.spec"
base_url = "https://prod.example.com"     # optional; overrides spec's recorded value

[spec.headers]
Authorization = "Bearer $OPENBB_UPSTREAM_TOKEN"
X-Tenant      = "production"
```

Config-supplied headers OVERRIDE matching incoming-request headers — `[spec.headers]` is the credential-injection point, so a misbehaving client can't leak its own auth value upstream by sending the same header name.

## Custom HTTP middleware (`[middleware]`)

Attach Starlette-style HTTP middleware functions from a config-supplied entrypoint — useful for auth, request logging, tracing, IP allow-listing, response transformation. Each entry is a `"module:async_callable"` reference resolved through the standard import system:

```toml
[middleware]
hooks = [
    "my_pkg.middleware:auth_middleware",
    "my_pkg.middleware:request_logger",
]
```

```python
# my_pkg/middleware.py
from fastapi.responses import JSONResponse

async def auth_middleware(request, call_next):
    if request.headers.get("X-API-Key") != "expected":
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    return await call_next(request)

async def request_logger(request, call_next):
    response = await call_next(request)
    print(f"{request.method} {request.url.path} → {response.status_code}")
    return response
```

List order is **outermost-to-innermost**: the first entry sees the request first on the way in and the response last on the way out. Misconfigured references (missing module, wrong attribute, sync function, wrong arity) raise loudly at startup so deployments fail fast instead of silently passing requests through unauthenticated.

## Single-file launch

Everything in this README — app source (`--app` or `--spec`), env injection, host/port, SSL, agents, middleware, credentials — can be set in one `openbb.toml` and launched without any other CLI flags:

```sh
openbb-api --config-file ./openbb.toml
```

```toml
[launcher]
host = "0.0.0.0"
port = 8443
ssl-keyfile  = "/etc/ssl/key.pem"
ssl-certfile = "/etc/ssl/cert.pem"

[env]
OPENBB_UPSTREAM_TOKEN = "$GITHUB_TOKEN"

[spec]
path = "./cli.spec"

[spec.headers]
Authorization = "Bearer $OPENBB_UPSTREAM_TOKEN"

[middleware]
hooks = ["my_pkg.middleware:auth_middleware"]
```

That's the whole deployment manifest.

## Config file (`openbb.toml`)

Set runtime arguments and inject environment variables from a TOML file — the same layered cascade `openbb-core` uses (pyproject → user-global → project → explicit → `.env` → real env vars). Container-friendly: every layer is optional, no `HOME` required, and an explicit path can be supplied via `--config-file`, `$OPENBB_API_CONFIG`, or `$OPENBB_CONFIG`.

```toml
[launcher]
host = "0.0.0.0"
port = 6900
agents-json = "/etc/openbb/agents.json"
exclude = ["/api/v1/admin/*"]

[env]
# Pushed into os.environ before any heavy import — useful for
# orchestrator-injected secrets (Kubernetes, docker -e, CI tokens).
# Real shell env vars are NEVER clobbered. Supports $VAR / ${VAR}
# substitution; entries with unresolved references are skipped with
# a warning rather than set to a literal "$MISSING".
OPENBB_GITHUB_TOKEN = "$GITHUB_TOKEN"
OPENBB_API_URL      = "https://${HOST}:${PORT}/v1"
```

```sh
openbb-api --config-file /etc/openbb/openbb.toml
```

CLI flags always win over TOML; TOML always wins over defaults.

## Common flags

| Flag | Purpose |
|---|---|
| `--app PATH` | Path to your FastAPI app (file, `module:name`, or factory) |
| `--name NAME` | App instance name (default `app`) |
| `--factory` | Treat the target as a factory function |
| `--spec PATH` | Path to an `openbb-cli` `.spec` file — synthesizes a proxy app forwarding to the spec's `base_url`. Mutually exclusive with `--app` |
| `--config-file PATH` | Explicit `openbb.toml` path |
| `--host`, `--port` | Bind address and port |
| `--editable` | Generate `widgets.json` if missing and re-load it from disk on every request — manual edits to the file go live without a server restart |
| `--widgets-json PATH` | Use a hand-edited `widgets.json` |
| `--apps-json PATH` | Path to the dashboard apps file (default `~/OpenBBUserData/workspace_apps.json`) |
| `--agents-json PATH` | Adds `/agents.json` to the API |
| `--exclude '["/api/v1/admin/*"]'` | JSON-encoded list of routes to drop from `widgets.json` |
| `--ssl-keyfile`, `--ssl-certfile` | Run over HTTPS |

Run `openbb-api --help` for the full list — uvicorn flags pass through verbatim.

## Building widgets — at a glance

The launcher infers each widget's shape from your route signature. Common patterns:

```python
from fastapi import FastAPI
from openbb_platform_api.response_models import (
    Data,
    MetricResponseModel,
    OmniWidgetResponseModel,
    PdfResponseModel,
)

app = FastAPI()

# Markdown — return a string
@app.get("/hello")
async def hello() -> str:
    """Tooltip from the docstring."""
    return "Hello, OpenBB!"

# Table — return a list of records or a typed Data subclass
@app.get("/rows")
async def rows() -> list[dict]:
    return [{"symbol": "AAPL", "price": 150.0}]

# Metric — single label/value/delta
@app.get("/score")
async def score() -> MetricResponseModel:
    return MetricResponseModel(label="Score", value=100, delta="1%")

# Chart — return a Plotly figure JSON
@app.get("/chart", openapi_extra={"widget_config": {"type": "chart"}})
async def chart() -> dict:
    from plotly.graph_objs import Bar, Figure
    return Figure(data=[Bar(x=["A"], y=[1])]).to_plotly_json()
```

Annotated `Data` models drive auto-generated table column definitions:

```python
from datetime import date
from openbb_platform_api.response_models import Data
from pydantic import Field

class MyRow(Data):
    when: date = Field(title="Date", description="Trading date")
    pct:  float = Field(
        title="Change",
        json_schema_extra={"x-widget_config": {"formatterFn": "percent", "renderFn": "greenRed"}},
    )

@app.get("/data")
async def data() -> list[MyRow]:
    return [MyRow(when=date.today(), pct=0.0125)]
```

PDFs, omni widgets, server-side row model (SSRM) tables, form submission widgets, and per-column overrides via `widget_config` are all supported. See the [docs](https://docs.openbb.co/odp/python/extensions/interface/openbb-api) for the full surface.

## HTTPS

Generate a self-signed cert and point the launcher at it:

```sh
openssl req -x509 -days 3650 -out localhost.crt -keyout localhost.key \
  -newkey rsa:4096 -nodes -sha256 -subj '/CN=localhost' \
  -extensions EXT -config <(printf "[dn]\nCN=localhost\n[req]\ndistinguished_name = dn\n[EXT]\nsubjectAltName=DNS:localhost\nkeyUsage=digitalSignature\nextendedKeyUsage=serverAuth")

openbb-api --ssl-keyfile localhost.key --ssl-certfile localhost.crt
```

The browser will warn about the untrusted cert — accept once, or add `localhost.crt` to the OS trust store.

## License

AGPL-3.0-only. © OpenBB.
