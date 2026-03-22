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

When first connecting, the server exposes a small set of **admin** tools for
discovering and activating the full catalog. Not all tools are active by default.

All visibility changes are **per-session** — each connected client maintains its
own active toolset, so multiple agents can operate independently.

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
    {"name": "equity_price_historical", "active": true, "description": "Get historical price data..."},
    {"name": "equity_price_quote", "active": false, "description": "Get current price quote..."}
]
```

The `active` field shows whether the tool is currently enabled. Inactive tools
cannot be called until activated, but they still show a short cached description
so they remain discoverable.

The `subcategory` argument is optional. Omit it to see all tools in the
category.

### Step 3 — Activate Tools

Call `activate_tools` with a list of tool names:

```json
// Input
{"tool_names": ["equity_price_quote", "equity_price_historical"]}

// Output
"Activated: equity_price_quote, equity_price_historical"
```

Tools that were already active are silently included. Unknown names are reported
in the response:

```
"Activated: equity_price_quote  Not found: nonexistent_tool"
```

### Step 4 — Activate an Entire Category

Call `activate_category` to bulk-activate all tools in a category (or subcategory):

```json
// Activate everything in equity
{"category": "equity"}

// Activate only equity/price tools
{"category": "equity", "subcategory": "price"}

// Output
"Activated 5 tools in 'equity'/'price': equity_price_historical, equity_price_quote, ..."
```

This is faster than listing tool names individually when you need a whole category.

### Step 5 — Deactivate Tools

Call `deactivate_tools` to disable tools no longer needed:

```json
{"tool_names": ["equity_price_quote"]}
```

This reduces noise in the active tool list and can improve context efficiency.

### When Discovery Is Disabled

If the server was started with `--no-tool-discovery`, the admin tools are not
available. All tools in `default_tool_categories` are permanently active.

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
| `chart` | `object \| null` | Chart data if `chart=true` was passed |
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

When a tool is called with `chart: true` (where supported), the chart field
contains a Plotly figure:

```json
"chart": {
    "content": { "data": [...], "layout": {...} },
    "fig": { "data": [...], "layout": {...} }
}
```

The `content` key contains the Plotly JSON that can be rendered directly.
Not all endpoints support charting.

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
    {"name": "develop_extension", "tags": ["skill"], "arguments": []},
    {"name": "build_workspace_app", "tags": ["skill"], "arguments": []},
    {"name": "configure_mcp_server", "tags": ["skill"], "arguments": []},
    {"name": "analyze_stock", "tags": ["analysis"], "arguments": [
        {"name": "symbol", "type": "str", "required": true},
        {"name": "focus", "type": "str", "required": false, "default": "fundamentals"}
    ]}
]
```

### Execute a Prompt

Call `execute_prompt` with the prompt name and any required arguments:

```json
// Input
{"prompt_name": "analyze_stock", "arguments": {"symbol": "AAPL"}}

// Output - rendered prompt content
{
    "messages": [
        {"role": "user", "content": "Analyze AAPL focusing on fundamentals..."}
    ]
}
```

Prompts with no arguments (like skills) return their full content as-is.
Prompts with arguments substitute the provided values into the template.

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
| **Tool not active** | Tool does not appear in the available tools list |
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

1. Activate the tool: `activate_tools(["equity_price_historical"])`
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

### Checking Data Coverage

When unsure what providers are available for an endpoint, look at the tool's
input schema — the `provider` parameter's `enum` lists all installed options.

### Using Charts

Pass `chart: true` to get a pre-built Plotly visualization:

```json
{"symbol": "AAPL", "provider": "fmp", "chart": true}
```

The `chart` field in the response contains the Plotly figure JSON.

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
    {"uri": "skill://work_with_server/SKILL.md", "name": "work_with_server"}
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
| `available_tools` | `category`, `subcategory?` | List of tools with active status and descriptions |
| `activate_tools` | `tool_names: list` | Status message |
| `deactivate_tools` | `tool_names: list` | Status message |
| `activate_category` | `category`, `subcategory?` | Status message with count and tool names |

### OBBject Response Structure

| Field | Always Present | Content |
|---|---|---|
| `id` | Yes | Request UUID |
| `results` | Yes | Data payload (list, dict, string, or null) |
| `provider` | Yes | Provider name or null |
| `warnings` | Yes | Warning list or null |
| `chart` | Yes | Chart data or null |
| `extra` | Yes | Metadata dict (may be empty) |
