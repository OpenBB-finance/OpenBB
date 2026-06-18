---
name: use_openbb_cli
description: This guide covers the `openbb` command-line surface — running commands, generating `.spec` files, dispatching against precomputed specs, and feeding spec output back into `openbb-mcp` for spec-driven proxy mode.
---

# Using the openbb-cli

`openbb-cli` ships the `openbb` console-script. It is a self-contained
front-end for the same `obb` namespace the MCP server exposes, plus a build
tool for generating reusable `.spec` files and full installable extension
packages.

Three console-scripts live on the v5 stack:

| Command | Package | Purpose |
|---|---|---|
| `openbb` | `openbb-cli` | Run commands, REPL, generate `.spec` files. |
| `openbb-mcp` | `openbb-mcp-server` | MCP server launcher (HTTP/SSE/stdio transports). |
| `openbb-build` | `openbb-core` | Register a newly installed extension into the `obb` namespace. |

This guide focuses on `openbb`.

---

## Installation

```
pip install openbb-cli
```

Pulls `openbb-core[pandas]`, `prompt-toolkit`, `rich`, and `httpx`.

---

## Execution Modes

`openbb` has six mutually-exclusive modes (the rest of the flags are shared
across modes).

| Mode flag | Purpose |
|---|---|
| *(default)* | Single-shot: dispatch one dotted command and exit with NDJSON on stdout. |
| `-i` / `--interactive` | Rich REPL with prompt-toolkit completion. |
| `--batch` | Read NDJSON requests from stdin; emit NDJSON responses to stdout. |
| `--generate-spec` | Fetch `openapi.json` from `--server` and write a precomputed `.spec` file to `--output`. |
| `--generate-extension` | Build a full installable OpenBB Platform extension package from a `.spec` file. |
| `--list-commands` / `--describe COMMAND` | Print the command catalog or one command's schema as JSON. |

### Single-shot

```bash
openbb equity.price.historical --symbol AAPL --provider yfinance
```

Output is one OBBject envelope as a JSON line (`{"id": ..., "results": ..., "provider": ...}`).
Exit code is `0` on success, `1` on a dispatch error, `2` on a usage error.

### Interactive REPL

```bash
openbb -i
```

Prompt-toolkit completion against the resolved command catalog. Same flag
surface — `--server` / `--spec` / `--header` etc. work identically.

### Batch (NDJSON in/out)

```bash
echo '{"command":"equity.price.quote","params":{"symbol":"AAPL"},"id":"a"}
{"command":"equity.price.quote","params":{"symbol":"MSFT"},"id":"b"}' \
  | openbb --batch
```

Each input line is one `Request`; each output line is the matching
`Response`. Use `--batch-concurrency N` (or `OPENBB_CLI_BATCH_CONCURRENCY`) to
control in-flight parallelism.

---

## Backend Selection

Three backends share the dispatch surface; selection priority is
`--spec` > `--server` > in-process `obb`.

| Backend | Trigger | Behavior |
|---|---|---|
| Local | (default) | `LocalDispatcher` resolves commands against the in-process `obb` namespace. Pays the heavy `import openbb` once at startup. |
| Remote HTTP | `--server URL` | `HttpDispatcher` proxies to an `openbb-platform-api` server. The heavy import lives on the server. |
| Spec-driven | `--spec [NAME=]PATH` | Skips OpenAPI fetch + parse entirely. The spec carries the server URL it was generated against and the per-command HTTP methods. |

```bash
openbb --server https://api.example.com economy.gdp
openbb --spec /etc/openbb/cli.spec economy.gdp
```

`--spec` is repeatable. Multiple `NAME=PATH` entries build a multi-spec
dispatcher and the REPL routes by leading namespace
(`congress.bill` → `congress` spec, `nyfed.markets.ambs` → `nyfed` spec).
A single unnamed `--spec PATH` keeps the flat (unprefixed) command surface.

---

## `.spec` Files

A `.spec` file is a precomputed JSON document encoding every command the
server exposes — URL path, HTTP method, parameter schema, response schema,
and a `content_sha256` integrity hash over the canonical-JSON body.

### Generating a spec

```bash
# From an openbb-platform-api server
openbb --generate-spec --server https://api.example.com --output cli.spec

# From a server using a non-default OpenAPI path
openbb --generate-spec \
  --server https://markets.example.com \
  --openapi-path /static/docs/markets-api.yml \
  --output markets.spec

# From a Socrata story (no OpenAPI involved — walks the story for datasetUid
# entries and emits one router namespace per dataset)
openbb --generate-spec \
  --socrata-story https://data.example.gov/path/to/story.json \
  --output socrata.spec
```

### Using a spec

After generation, every dispatch can use the spec to skip OpenAPI fetch +
parse on every call:

```bash
openbb --spec cli.spec economy.gdp
openbb --spec cli.spec --list-commands
openbb --spec cli.spec --describe equity.price.historical
```

The spec's recorded `base_url` is the default upstream; pass `--server URL`
to override at dispatch time.

### Filtering commands at generation

`--include` and `--exclude` are repeatable glob patterns over dotted command
names. When `--include` is supplied it takes priority — anything not matching
is dropped regardless of `--exclude`.

```bash
openbb --generate-spec \
  --server https://api.example.com \
  --output equity.spec \
  --include 'equity.*' \
  --exclude 'equity.fundamentals.*'
```

---

## Headers and Query Parameters

Every dispatch (and the OpenAPI fetch during `--generate-spec`) carries the
same headers/query-params.

```bash
# Per-flag, repeatable
openbb --server https://api.example.com \
  -H 'Authorization: Bearer xxx' \
  -H 'X-Tenant: acme' \
  -Q 'api_key=secret' \
  equity.price.quote --symbol AAPL

# From a JSON file (object of string values)
openbb --header-file ./headers.json --query-param-file ./query.json economy.gdp
```

Env-var auto-loading: any `OPENBB_HTTP_QUERY_*` env var becomes a query param
(`OPENBB_HTTP_QUERY_API_KEY=xxx` → `?api_key=xxx`). CLI flags beat env vars.

For multi-spec dispatchers, headers can be scoped per namespace via the TOML
config (`[specs.<ns>.headers]`).

---

## Configuration File (`openbb.toml`)

Flag defaults can be set via a layered TOML cascade — same pattern openbb-core
uses. Layers (highest priority last):

```
pyproject.toml [tool.openbb-cli]
  → user-global ~/.openbb_platform/openbb.toml
  → project openbb.toml (walking up from CWD)
  → --config PATH (explicit)
  → .env files
  → real shell env vars
```

CLI flags always beat env vars; env vars beat TOML.

```toml
# openbb.toml
[openbb-cli]
server = "https://api.example.com"
batch_concurrency = 8

[openbb-cli.headers]
Authorization = "Bearer $OPENBB_UPSTREAM_TOKEN"

[specs.congress]
path = "/etc/openbb/congress.spec"
[specs.congress.headers]
"X-API-Key" = "$CONGRESS_KEY"
```

```bash
openbb --config /etc/openbb/openbb.toml --list-commands
openbb --print-config-template      # documented TOML template
openbb --show-config                # merged config as JSON
```

---

## Building Extensions From a Spec

`--generate-extension` builds a full installable OpenBB Platform extension
package from a `.spec` file. Each spec becomes one provider with its own
router; `pip install -e <output>` + `openbb-build` registers it.

```bash
openbb --generate-extension \
  --spec congress.spec \
  --output ./openbb-congress-gov \
  --provider-name congress_gov \
  --project-name openbb-congress-gov \
  --package-name openbb_congress_gov \
  --router-name congress

pip install -e ./openbb-congress-gov
openbb-build
```

After registration the extension's commands are reachable via `obb.congress.*`
in Python and `congress.*` from any backend.

---

## Spec → MCP Round-Trip

The same `.spec` file can drive the MCP server in spec-driven proxy mode —
the heavy `import openbb` lives on the upstream `openbb-platform-api`, the
MCP launcher only knows the spec.

```bash
# 1. Generate the spec on the host that already has openbb installed.
openbb --generate-spec --server https://api.example.com --output cli.spec

# 2. Hand off the spec to a lightweight MCP container.
openbb-mcp --spec /etc/openbb/cli.spec
```

Or via TOML:

```toml
# openbb.toml passed via `openbb-mcp --config-file openbb.toml`
[mcp.spec]
path = "/etc/openbb/cli.spec"
content_sha256 = "abc..."

[mcp.spec.headers]
Authorization = "Bearer $OPENBB_UPSTREAM_TOKEN"
```

The MCP server synthesizes a FastAPI proxy app from the spec's commands;
FastMCP exposes the routes as MCP tools; per-tool dispatch forwards to the
spec's `base_url` over `aiohttp`. See `configure_mcp_server` for multi-spec
mounts (`[mcp.spec.NAME]`), per-spec auth/middleware hooks, and the
`content_sha256` provenance pin.

---

## Useful Environment Variables

| Variable | Purpose |
|---|---|
| `OPENBB_SERVER_URL` | Default `--server` URL. |
| `OPENBB_SPEC_PATH` | Default `--spec` path. |
| `OPENBB_HTTP_QUERY_*` | Auto-loaded as query parameters (`OPENBB_HTTP_QUERY_API_KEY=xxx` → `?api_key=xxx`). |
| `OPENBB_CLI_CONFIG` | Default `--config` path. |
| `OPENBB_CLI_ENV_FILE` | Default `--env-file` path. |
| `OPENBB_CLI_BATCH_CONCURRENCY` | Default `--batch-concurrency`. |
| `OPENBB_HEADER_FILE` / `OPENBB_QUERY_PARAM_FILE` | Default `--header-file` / `--query-param-file`. |

`~/.openbb_platform/.env` is always loaded as a fallback `.env` source — real
shell exports beat both.

---

## Quick Reference

```bash
# Discover commands
openbb --list-commands
openbb --describe equity.price.historical

# One-shot dispatch
openbb equity.price.historical --symbol AAPL --provider yfinance

# Batch (NDJSON)
cat requests.ndjson | openbb --batch

# Generate a precomputed spec from a server
openbb --generate-spec --server URL --output out.spec

# Dispatch through a precomputed spec
openbb --spec out.spec equity.price.quote --symbol AAPL

# Multi-spec routing by leading namespace
openbb --spec congress=congress.spec --spec nyfed=nyfed.spec congress.bill

# Generate a full extension package from a spec
openbb --generate-extension --spec out.spec --output ./openbb-myprov

# Inspect resolved config
openbb --show-config
openbb --print-config-template > openbb.toml
```
