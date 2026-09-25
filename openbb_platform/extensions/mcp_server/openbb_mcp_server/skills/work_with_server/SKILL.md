---
name: work_with_server
description: This guide explains how to call tools, interpret responses, discover capabilities, use prompts, and handle errors when interacting with an OpenBB MCP server.
---

# Working With the OpenBB MCP Server

This guide explains how to call tools, interpret responses, discover
capabilities, use prompts, and handle errors when interacting with an OpenBB
MCP server.

---

## Tool Discovery Workflow

When the server runs with `--tool-discovery`, the OpenBB tools are left out of
the tool list, and a small set of discovery tools finds and runs them.

Discovery holds no per-session state — every client sees the same tool list, and
nothing needs to be activated before a call.

### Step 1 — List Categories

Call `available_categories` (no arguments) to see what is installed:

```json
[
    {
        "name": "equity",
        "subcategories": [
            {"name": "price", "tool_count": 5},
            {"name": "fundamental", "tool_count": 12}
        ],
        "total_tools": 17
    },
    {
        "name": "economy",
        "subcategories": [
            {"name": "general", "tool_count": 3}
        ],
        "total_tools": 3
    }
]
```

Each category maps to a top-level API router. Subcategories are nested routers.

### Step 2 — Browse Tools in a Category

Call `available_tools` with a category name:

```json
// Input
{"category": "equity", "subcategory": "price"}

// Output
[
    {"name": "equity_price_historical", "description": "Get historical price data..."},
    {"name": "equity_price_quote", "description": "Get current price quote..."}
]
```

Each entry has the tool's name and a one-sentence description. The
`subcategory` argument is optional. Omit it to see all tools in the category.

### Step 3 — Search for Tools

Call `search_tools` with a natural-language query:

```json
// Input
{"query": "historical stock prices"}

// Output - full tool definitions, in the same format as list_tools
[
    {"name": "equity_price_historical", "description": "...", "inputSchema": {"...": "..."}}
]
```

Search covers the hidden OpenBB tools and returns at most five matches. Use
each match's `inputSchema` to build the arguments.

### Step 4 — Call a Tool

Call `call_tool` with the tool name and its arguments:

```json
{"name": "equity_price_historical", "arguments": {"symbol": "AAPL", "provider": "yfinance"}}
```

`call_tool` runs the named tool and returns its result. A hidden tool can also
be called directly by name, with the same arguments.

### When Discovery Is Disabled

If the server was started without `--tool-discovery`, the discovery tools are not
available. All tools in `default_tool_categories` are listed and called directly;
tools outside them are not served, and calling one fails with "Unknown tool".

---

## openbb-cli Dispatcher Tools

When the optional `openbb-mcp-server[cli]` extra is installed (it pulls in
`openbb-cli`), the server also registers four first-class tools that wrap
`openbb-cli`'s NDJSON dispatcher protocol. They give an agent the same
`obb`-namespace command surface that the `openbb` CLI exposes — without
shelling out or standing up a Python REPL.

### `openbb_dispatch`

Execute a single command and return its serialized result.

```json
{
    "name": "openbb_dispatch",
    "arguments": {
        "command": "equity.price.historical",
        "params": {"symbol": "AAPL", "provider": "yfinance"},
        "server_url": null
    }
}
```

| Argument | Type | Notes |
|---|---|---|
| `command` | `string` | Dotted command path under the `obb` namespace (e.g. `equity.price.historical`). |
| `params` | `dict \| null` | Keyword arguments forwarded to the command. Defaults to `{}`. |
| `server_url` | `string \| null` | When set, dispatches against a remote `openbb-platform-api` server (HTTP). When omitted, falls back to `OPENBB_SERVER_URL`, then in-process local dispatch. |

The result is a dispatcher response. `ok` reports success, `result` holds the
command's OBBject fields (`results`, `provider`, ...), and `error` carries the
`type` and `message` of a failure instead of raising:

```json
{
    "id": null,
    "ok": true,
    "result": {"results": [{"date": "2025-01-02", "close": 243.85}], "provider": "yfinance"},
    "error": null
}
```

Remote dispatch unwraps a single-row `results` list to the row itself.

### `openbb_batch_dispatch`

Execute many commands concurrently and return results in input order.

```json
{
    "name": "openbb_batch_dispatch",
    "arguments": {
        "requests": [
            {"command": "equity.price.quote", "params": {"symbol": "AAPL"}, "id": "a"},
            {"command": "equity.price.quote", "params": {"symbol": "MSFT"}, "id": "b"}
        ]
    }
}
```

Each entry needs `command` (dotted path); `params` and `id` are optional. The
`id` is opaque correlation echoed back on the matching response. Failures
surface as response objects with `ok=False` and a structured `error` block —
no exception bubbles up, errors are per-request.

### `openbb_list_commands`

List every command with a one-line description. Takes only the optional
`server_url`. The response's `result` is a list of `{"name", "description"}`
entries. Equivalent to `openbb --list-commands` on the CLI.

### `openbb_describe_command`

Return one command's parameters and output schema.

```json
{
    "name": "openbb_describe_command",
    "arguments": {"command": "equity.price.historical", "provider": "yfinance"}
}
```

The response's `result` has the command `name`, its `parameters` (each with
`name`, `in`, and `type`, plus `required`, `default`, `choices`, and `help` when
set), and its `output_schema`. For a command with several providers, pass
`provider` to get that provider's `parameters` and `output_schema`; without it,
`result.providers` maps every provider to its own `parameters` and
`output_schema`. Equivalent to `openbb --describe equity.price.historical`
(`equity.price.historical:yfinance` for one provider) on the CLI.

### Local vs remote dispatch

| Mode | Trigger | Behavior |
|---|---|---|
| Local | No `server_url`, no `OPENBB_SERVER_URL` | `LocalDispatcher` resolves commands against the in-process `obb` namespace. Pays the heavy `import openbb` once at startup. Single-tenant. |
| Remote | `server_url` arg or `OPENBB_SERVER_URL` env | `HttpDispatcher` proxies commands to a long-running `openbb-platform-api` server. Multi-tenant; the heavy import lives on the server. |

Mode is per-call — different requests in the same session can target different
servers. Dispatchers are cached for the server's lifetime, so the `import openbb`
cost (local) and the remote server's OpenAPI download are paid once per target.

---

## Calling Data Tools

### Input Parameters

Every data tool has a JSON Schema describing its input. A typical tool schema:

```json
{
    "type": "object",
    "properties": {
        "symbol": {
            "type": "string",
            "description": "Symbol to get data for."
        },
        "provider": {
            "type": "string",
            "enum": ["fmp", "polygon", "yfinance"],
            "description": "The provider to use for the query."
        },
        "start_date": {
            "anyOf": [{"type": "string", "format": "date"}, {"type": "null"}],
            "description": "Start date of the data."
        },
        "end_date": {
            "anyOf": [{"type": "string", "format": "date"}, {"type": "null"}],
            "description": "End date of the data."
        },
        "interval": {
            "type": "string",
            "default": "1d",
            "description": "Time interval of the data."
        }
    },
    "required": ["symbol"]
}
```

Key rules:

- **`provider`** — present only on endpoints that use the provider interface.
  When listed, its enum shows available provider sources. If the endpoint has
  only one provider, you can omit it and the sole provider is used
  automatically. When multiple providers are available, select one from the
  enum. Different providers may return different fields or support different
  parameters. Endpoints that do not use the provider interface (basic GET/POST
  routes) have no `provider` parameter at all.
- **`symbol` formatting** — symbols are case-insensitive. Multiple symbols can
  be comma-separated: `"AAPL,MSFT,GOOG"`.
- **Dates** — always formatted as `YYYY-MM-DD` strings.
- **Optional parameters** — have `anyOf` with a `null` type or a `default`
  value. Omit them to use defaults.
- **Provider-specific parameters** — some parameters are only relevant for
  certain providers. The schema unions all of them; irrelevant ones are
  silently ignored.
- **Valid values** — never guess a value. A parameter with a fixed set of
  values has an `enum`. When the values differ by provider, or several can be
  comma-separated, the description lists them (`Valid values by provider:
  ...`, `Valid values for provider oecd (comma-separate several): ...`). When
  another tool lists them, the description names it and its arguments
  (``Get the valid values from the `derivatives_options_strikes` tool with
  symbol=<the symbol you pass here>.``) — call that tool first.

### Example Tool Call

```json
{
    "name": "equity_price_historical",
    "arguments": {
        "symbol": "AAPL",
        "provider": "fmp",
        "start_date": "2025-01-01",
        "end_date": "2025-02-01",
        "interval": "1d"
    }
}
```

---

## Understanding the Response

Every OpenBB tool returns an **OBBject** — a standardized response envelope:

```json
{
    "id": "06520558-d54a-7e53-8000-7aafc8a42694",
    "results": [...],
    "provider": "fmp",
    "warnings": null,
    "chart": null,
    "extra": {
        "metadata": {
            "arguments": {...},
            "duration": 565256375,
            "route": "/equity/price/historical",
            "timestamp": "2025-01-15 11:28:57.149548"
        }
    }
}
```

### Response Fields

| Field | Type | Description |
|---|---|---|
| `id` | `string` | UUID identifying this request |
| `results` | `list[dict] \| dict \| string \| null` | The actual data. Usually a list of records |
| `provider` | `string \| null` | Which provider fulfilled the request |
| `warnings` | `list[object] \| null` | Non-fatal warnings from the provider or platform |
| `chart` | `object \| null` | Chart artifact if `chart=true` was passed |
| `extra` | `dict` | Execution metadata and results metadata |

### The `results` Field

This is the primary data payload. Its structure depends on the endpoint:

**Tabular data** — most common, a list of dictionaries (one per row):

```json
"results": [
    {"date": "2025-01-02", "open": 150.0, "high": 155.0, "low": 149.0, "close": 153.5, "volume": 1000000},
    {"date": "2025-01-03", "open": 153.0, "high": 157.0, "low": 152.0, "close": 156.2, "volume": 1200000}
]
```

**Single record** — some endpoints return a single dict:

```json
"results": {"symbol": "AAPL", "price": 185.50, "change": 2.30, "volume": 45000000}
```

**Empty results** — when no data is available:

```json
"results": null
```

or

```json
"results": []
```

**Field names vary by provider** — different providers may return different
columns for the same endpoint. Always check the keys in the returned records.

### The `warnings` Field

Warnings are non-fatal issues that occurred during execution:

```json
"warnings": [
    {
        "category": "OpenBBWarning",
        "message": "Parameter 'source' is not supported by fmp. Available for: intrinio."
    }
]
```

Common warning scenarios:
- Unknown parameters silently ignored by the provider
- Partial data returned (fewer rows than requested)
- Provider-specific data quality notes

When `warnings` is `null`, no warnings were generated.

### The `extra` Field

Contains execution metadata and optional results metadata:

```json
"extra": {
    "metadata": {
        "arguments": {
            "provider_choices": {"provider": "fmp"},
            "standard_params": {"symbol": "AAPL", "start_date": "2025-01-01"},
            "extra_params": {}
        },
        "duration": 565256375,
        "route": "/equity/price/historical",
        "timestamp": "2025-01-15 11:28:57.149548"
    },
    "results_metadata": {
        "...provider-specific metadata..."
    }
}
```

**`metadata`** — always present (unless disabled):
- `arguments` — the exact parameters used, split into provider choices,
  standard params, and extra (provider-specific) params
- `duration` — nanoseconds the request took
- `route` — the API endpoint path
- `timestamp` — when the request was made

**`results_metadata`** — present when the provider returns contextual
information about the data (e.g., FRED series metadata, CBOE options
metadata). Contents vary by endpoint and provider.

### The `chart` Field

When a tool is called with `chart: true` (where supported), the server
replaces the Plotly figure with an OpenBB Workspace artifact:

```json
"chart": {
    "type": "chart",
    "name": "AAPL Close",
    "description": "Output of the equity_price_historical tool.",
    "uuid": "5b0e1c52-6f3e-4a51-9d6f-0f1b6a2f4c11",
    "content": [{"date": "2025-01-02", "close": 243.85}],
    "chart_params": {"chartType": "line", "xKey": "date", "yKey": ["close"]}
}
```

`content` holds the rows the chart is drawn from and `chart_params` says how:
`chartType` is `line`, `bar`, or `scatter` with `xKey` and `yKey`, or `pie`
or `donut` with `angleKey` and `calloutLabelKey`. Figures that cannot be
drawn that way (surfaces, candlesticks, heatmaps) come back as a `table`
artifact of their data, without `chart_params`. Tools that return a figure
directly return the artifact as their whole output. Present the artifact
as it is; do not convert it or re-plot it. Not all endpoints support
charting.

---

## Provider Selection

### How Providers Work

Each data endpoint can have multiple provider sources (e.g., FMP, Yahoo Finance,
Polygon). Providers differ in:

- **Available parameters** — some providers offer extra filtering or options
- **Returned fields** — column names and data granularity may differ
- **Rate limits and authentication** — some providers require API keys
- **Data coverage** — geographic markets, date ranges, asset types

### Choosing a Provider

When a tool's input schema includes `provider`, its enum lists all installed
provider sources for that endpoint. If there is only one provider, the
parameter can be omitted — the sole provider is selected automatically.
When multiple providers are available, pick one based on:

1. **Check the enum** — only listed options work
2. **Consider the data need** — different providers may have different fields
3. **API key requirements** — some providers need credentials configured in
   `~/.openbb_platform/user_settings.json`

Endpoints that do not use the provider interface (basic GET/POST routes added
via `router.command(methods=["GET"])` or raw FastAPI) have no `provider`
parameter.

If a provider fails due to missing credentials, the error message will indicate
an authentication issue.

### Provider-Specific Parameters

Some parameters only apply to certain providers. For example, the `source`
parameter might only be available with the `intrinio` provider. Passing it to
`fmp` generates a warning but does not cause an error.

---

## Working With Prompts

The server includes a prompt system for accessing documentation, usage guides,
and analysis frameworks.

### List Available Prompts

Call `list_prompts` (no arguments):

```json
[
    {"name": "system_prompt", "description": "System prompt with guidance...", "arguments": []},
    {"name": "analyze_stock", "description": "Analyze a stock.", "arguments": [
        {"name": "symbol", "description": "Ticker.", "required": true},
        {"name": "focus", "description": "Area.", "required": false}
    ]}
]
```

### Get a Prompt

Call `get_prompt` with the prompt `name` and any `arguments`:

```json
// Input
{"name": "analyze_stock", "arguments": {"symbol": "AAPL"}}

// Output - the rendered prompt
{
    "messages": [
        {"role": "user", "content": "Analyze AAPL focusing on fundamentals."}
    ]
}
```

Pass every argument value as a string (`{"years": "10"}`, not `{"years": 10}`);
MCP prompt arguments are strings. Prompts without arguments return their
content as-is. Omitted optional arguments fall back to their defaults, and a
missing required argument is an error. Skills are resources, not prompts; see
[Working With Skills](#working-with-skills).

### Prompt Categories by Tag

| Tag | Source | Description |
|---|---|---|
| `system` | System prompt file | Server-wide context and instructions |
| `server` | Server prompts JSON | Reusable analysis frameworks |
| `route-specific` | Inline on API routes | Endpoint usage guides |

---

## Error Handling

### Error Types

| Scenario | What Happens |
|---|---|
| **Invalid parameters** | Error with HTTP 422 details explaining which parameter failed validation |
| **Missing required parameter** | Error with HTTP 422 indicating the missing field |
| **Provider authentication failure** | Error with HTTP 401/403 indicating credentials are missing or invalid |
| **Provider rate limit** | Error with HTTP 429 or provider-specific rate limit message |
| **No data available** | Successful response with `results: null` or `results: []` |
| **Tool hidden by discovery** | Tool is not in the tool list; find it with `search_tools` and run it with `call_tool` |
| **Tool outside the served categories** | "Unknown tool" error, by name, through `call_tool`, and through `run_pipeline` |
| **Unknown tool name** | Standard MCP protocol error |
| **Category not found** (discovery) | Error listing available categories |
| **Connection failure** | Error with "Request error: ..." |

### Interpreting Empty Results

A response with `results: null` or `results: []` is **not an error** — it
means the provider had no data matching the query. Common causes:

- Date range with no trading days
- Symbol not covered by the selected provider
- Data not yet available for the requested period

Try a different provider, adjust the date range, or verify the symbol format.

### Reading Validation Errors

Validation errors (HTTP 422) include detail about what went wrong:

```
HTTP error 422: Unprocessable Entity - {"detail": [{"loc": ["query", "symbol"], "msg": "field required", "type": "value_error.missing"}]}
```

The `loc` field shows which parameter failed, and `msg` explains why.

---

## Practical Patterns

### Fetching Time Series Data

1. With discovery enabled, find the tool: `search_tools({"query": "historical stock prices"})`
2. Call with date range:
   ```json
   {"symbol": "AAPL", "provider": "fmp", "start_date": "2025-01-01", "end_date": "2025-02-01"}
   ```
3. Read `results` — each record has `date`, `open`, `high`, `low`, `close`,
   `volume` (field names depend on provider)

### Comparing Multiple Symbols

Pass comma-separated symbols:

```json
{"symbol": "AAPL,MSFT,GOOG", "provider": "fmp"}
```

Results will contain records for all symbols. Filter by the `symbol` field in
each record if present, or by the ordering pattern.

### Chaining Tool Calls

Use the output of one tool as input to another:

1. Get peers: `equity_compare_peers({"symbol": "AAPL", "provider": "fmp"})`
2. Extract symbols from `results`
3. Get quotes: `equity_price_quote({"symbol": "AAPL,PEER1,PEER2", "provider": "fmp"})`

When a later tool needs the earlier tool's rows rather than a few values picked
from them, use `run_pipeline` (below) so the rows never pass through the
conversation.

### Running Data-Processing Tools With `run_pipeline`

Technical, quantitative, and econometrics tools (`technical_rsi`,
`technical_macd`, ...) take the rows to analyze as a `data` argument. Fetch and
analyze in one `run_pipeline` call instead of copying a price history into
their arguments:

```json
{
    "steps": [
        {
            "id": "prices",
            "tool": "equity_price_historical",
            "arguments": {"symbol": "AAPL", "provider": "yfinance", "start_date": "2025-01-01"}
        },
        {"id": "rsi", "tool": "technical_rsi", "arguments": {"length": 14}, "inputs": {"data": "prices"}},
        {"id": "macd", "tool": "technical_macd", "inputs": {"data": "prices"}}
    ],
    "outputs": ["rsi", "macd"]
}
```

- Each step has a `tool`, its `arguments`, an optional `id`, and `inputs`, which
  maps an argument name to the `id` of an earlier step. That step's `results`
  fill the argument (its whole output when it has no `results`).
- A step without an `id` is referred to by its position (`"0"`, `"1"`, ...).
- `outputs` lists the steps to return; by default only the last step comes back.
- The request is validated before any step runs. A failing step is reported as
  `Step '<id>' (<tool>) failed: ...`.
- With tool discovery, use `search_tools` to find the tools and their
  parameters; `run_pipeline` can call tools hidden by discovery by name, but
  not tools outside the categories the server serves.

### Checking Data Coverage

When unsure what providers are available for an endpoint, look at the tool's
input schema — the `provider` parameter's `enum` lists all installed options.

### Using Charts

Pass `chart: true` to get a pre-built visualization:

```json
{"symbol": "AAPL", "provider": "fmp", "chart": true}
```

The `chart` field in the response holds a `chart` or `table` artifact (see
The `chart` Field). In `run_pipeline`, a step that returns an artifact passes
its `content` rows to later steps.

---

## User Settings and Defaults

The server reads user settings from `~/.openbb_platform/user_settings.json`:

### API Keys

Provider credentials are stored under `credentials`:

```json
{
    "credentials": {
        "fmp_api_key": "YOUR_KEY",
        "polygon_api_key": "YOUR_KEY"
    }
}
```

Without the required API key, calls to that provider will fail with an
authentication error.

### Default Provider

Set a default provider per endpoint so it is preselected:

```json
{
    "defaults": {
        "commands": {
            "/equity/price/historical": {"provider": "yfinance"},
            "/economy/cpi": {"provider": "oecd"}
        }
    }
}
```

When multiple providers are available, this determines the default selection
if the parameter is omitted.

### Default Parameters

Individual parameters can be defaulted so they are applied when not explicitly
passed:

```json
{
    "defaults": {
        "commands": {
            "/equity/price/historical": {
                "provider": "fmp",
                "chart": true,
                "chart_params": {
                    "heikin_ashi": true,
                    "indicators": {"sma": {"length": [21, 50]}}
                }
            }
        }
    }
}
```

### Output Preferences

The `output_type` preference controls how the Python Interface returns data.
For MCP, the server always returns the full OBBject JSON regardless of this
setting, but it is relevant for the Python Interface:

| Output Type | Description |
|---|---|
| `OBBject` | Full response object (default) |
| `dataframe` | Pandas DataFrame |
| `numpy` | NumPy array |
| `dict` | Python dictionary |
| `polars` | Polars DataFrame |
| `llm` | JSON-encoded string of results only |
| `chart` | Chart object |

### LLM Mode

Setting `output_type` to `"llm"` in the Python Interface strips everything
except `results` and returns it as a JSON string. This is optimized for token
efficiency in LLM frameworks. In the REST API / MCP context, the full OBBject
is always returned.

---

## Working With Skills

Skills are MCP resources exposed at `skill://<name>/SKILL.md` URIs. Discover
and read them via the standard MCP resource methods.

### Discover Available Skills

Call `list_resources()` (no arguments):

```json
[
    {"uri": "skill://develop_extension/SKILL.md", "name": "develop_extension"},
    {"uri": "skill://build_workspace_app/SKILL.md", "name": "build_workspace_app"},
    {"uri": "skill://configure_mcp_server/SKILL.md", "name": "configure_mcp_server"},
    {"uri": "skill://work_with_server/SKILL.md", "name": "work_with_server"},
    {"uri": "skill://use_openbb_cli/SKILL.md", "name": "use_openbb_cli"}
]
```

### Read a Skill

Call `read_resource()` with the skill URI:

```json
// Input
{"uri": "skill://develop_extension/SKILL.md"}

// Output — full Markdown content of the skill guide
```

### Supporting Files

Skill directories can contain additional supporting files (e.g. templates,
examples). Reference the skill manifest at `skill://<name>/_manifest` to
discover any supporting files packaged alongside the main `SKILL.md`.

---

## Quick Reference

### Admin Tools (Discovery)

| Tool | Input | Returns |
|---|---|---|
| `available_categories` | *(none)* | List of categories with subcategories and tool counts |
| `available_tools` | `category`, `subcategory?` | List of tools with names and descriptions |
| `search_tools` | `query` | Full definitions of the matching tools |
| `call_tool` | `name`, `arguments?` | The tool's result |

### Pipeline Tool (Always Listed)

| Tool | Input | Returns |
|---|---|---|
| `run_pipeline` | `steps`, `outputs?` | Outputs of the selected steps, keyed by step id |

### OBBject Response Structure

| Field | Always Present | Content |
|---|---|---|
| `id` | Yes | Request UUID |
| `results` | Yes | Data payload (list, dict, string, or null) |
| `provider` | Yes | Provider name or null |
| `warnings` | Yes | Warning list or null |
| `chart` | Yes | Chart artifact or null |
| `extra` | Yes | Metadata dict (may be empty) |
