---
name: configure_mcp_server
description: This guide covers installation, configuration, authentication, tool discovery, prompt management, and client integration for `openbb-mcp-server`.
---

# Configure and Build the OpenBB MCP Server

This guide covers installation, configuration, authentication, tool discovery,
prompt management, and client integration for `openbb-mcp-server`.

---

## Installation

```
pip install openbb-mcp-server
```

This installs the `openbb-mcp` CLI command. To include the default OpenBB
extensions as tools, also install them:

```
pip install openbb
```

Or install individual extensions:

```
pip install openbb-equity openbb-economy
```

---

## Starting the Server

### Default (all installed OpenBB extensions)

```
openbb-mcp
```

Defaults: `--host 127.0.0.1 --port 8001 --transport streamable-http`

### With a Custom FastAPI Application

```
# File path with default instance name "app"
openbb-mcp --app ./my_app.py

# Explicit instance name
openbb-mcp --app ./my_app.py --name my_app

# Module import syntax
openbb-mcp --app my_package.app:my_app

# Factory function pattern
openbb-mcp --app ./my_app.py:create_app --factory
```

### Transport Options

| Transport | Flag | Use Case |
|---|---|---|
| `streamable-http` | `--transport streamable-http` | Default. HTTP-based, works with Cursor, VS Code |
| `sse` | `--transport sse` | Legacy Server-Sent Events. Required by Cline |
| `stdio` | `--transport stdio` | Standard I/O. Used by Claude Desktop |

---

## CLI Arguments

| Argument | Description | Default |
|---|---|---|
| `--app <path>` | Path to FastAPI application file or `module:instance` | OpenBB default app |
| `--name <name>` | Name of the FastAPI instance or factory function | `app` |
| `--factory` | Treat `--name` as a factory function | `false` |
| `--host <host>` | Server host | `127.0.0.1` |
| `--port <port>` | Server port | `8001` |
| `--transport <type>` | `streamable-http`, `sse`, or `stdio` | `streamable-http` |
| `--default-categories <csv>` | Comma-separated default active tool categories | `all` |
| `--allowed-categories <csv>` | Restrict available categories to this list | All categories |
| `--no-tool-discovery` | Disable runtime tool activation/deactivation | Discovery enabled |
| `--system-prompt <path>` | Path to a `.txt` system prompt file | None |
| `--server-prompts <path>` | Path to a `.json` server prompts file | None |

Any additional `--key value` pairs are forwarded to Uvicorn as config.

---

## Configuration Precedence

Settings are resolved in this order (highest priority first):

1. **CLI arguments** — command-line flags
2. **Environment variables** — prefixed with `OPENBB_MCP_`
3. **Config file** — `~/.openbb_platform/mcp_settings.json`
4. **Defaults** — built-in MCPSettings defaults

### Config File Example

Create `~/.openbb_platform/mcp_settings.json`:

```json
{
    "name": "My MCP Server",
    "default_tool_categories": ["equity", "economy"],
    "enable_tool_discovery": true,
    "describe_responses": false,
    "system_prompt_file": "/path/to/system_prompt.txt",
    "server_prompts_file": "/path/to/prompts.json"
}
```

### Environment Variables

All settings map to `OPENBB_MCP_` prefixed environment variables:

```
OPENBB_MCP_NAME="My MCP Server"
OPENBB_MCP_DEFAULT_TOOL_CATEGORIES="equity,economy,crypto"
OPENBB_MCP_ENABLE_TOOL_DISCOVERY=true
OPENBB_MCP_SYSTEM_PROMPT_FILE="/path/to/prompt.txt"
OPENBB_MCP_SERVER_PROMPTS_FILE="/path/to/prompts.json"
```

---

## Settings Reference

### Server Identity

| Setting | Env Var | Type | Default |
|---|---|---|---|
| `name` | `OPENBB_MCP_NAME` | `str` | `"OpenBB MCP"` |
| `description` | `OPENBB_MCP_DESCRIPTION` | `str` | Auto-generated |
| `version` | `OPENBB_MCP_VERSION` | `str \| None` | `None` |

### Tool Configuration

| Setting | Env Var | Type | Default |
|---|---|---|---|
| `default_tool_categories` | `OPENBB_MCP_DEFAULT_TOOL_CATEGORIES` | `list[str]` | `["all"]` |
| `allowed_tool_categories` | `OPENBB_MCP_ALLOWED_TOOL_CATEGORIES` | `list[str] \| None` | `None` |
| `enable_tool_discovery` | `OPENBB_MCP_ENABLE_TOOL_DISCOVERY` | `bool` | `true` |
| `list_page_size` | `OPENBB_MCP_LIST_PAGE_SIZE` | `int \| None` | `None` |
| `describe_responses` | `OPENBB_MCP_DESCRIBE_RESPONSES` | `bool` | `false` |
| `api_prefix` | `OPENBB_MCP_API_PREFIX` | `str \| None` | `None` |

### Prompt Configuration

| Setting | Env Var | Type | Default |
|---|---|---|---|
| `system_prompt_file` | `OPENBB_MCP_SYSTEM_PROMPT_FILE` | `str \| None` | `None` |
| `server_prompts_file` | `OPENBB_MCP_SERVER_PROMPTS_FILE` | `str \| None` | `None` |
| `default_skills_dir` | `OPENBB_MCP_DEFAULT_SKILLS_DIR` | `str \| None` | Built-in skills dir |
| `skills_reload` | `OPENBB_MCP_SKILLS_RELOAD` | `bool` | `false` |
| `skills_providers` | `OPENBB_MCP_SKILLS_PROVIDERS` | `list[str] \| None` | `None` |

### HTTP Transport

| Setting | Env Var | Type | Default |
|---|---|---|---|
| `uvicorn_config` | `OPENBB_MCP_UVICORN_CONFIG` | `dict` | `{"host": "127.0.0.1", "port": "8001"}` |

### Duplicate Handling

| Setting | Env Var | Type | Default |
|---|---|---|---|
| `on_duplicate_tools` | `OPENBB_MCP_ON_DUPLICATE_TOOLS` | `str \| None` | `None` |
| `on_duplicate_resources` | `OPENBB_MCP_ON_DUPLICATE_RESOURCES` | `str \| None` | `None` |
| `on_duplicate_prompts` | `OPENBB_MCP_ON_DUPLICATE_PROMPTS` | `str \| None` | `None` |

Options: `"warn"`, `"error"`, `"replace"`, `"ignore"`

### Module Exclusion

| Setting | Env Var | Type | Default |
|---|---|---|---|
| `module_exclusion_map` | `OPENBB_MCP_MODULE_EXCLUSION_MAP` | `dict \| None` | Auto-detected |

By default, categories whose Python modules cannot be imported are excluded
(e.g., `econometrics`, `quantitative`, `technical`, `coverage`).

---

## Authentication

Three authentication modes are available.

### Server-Side Authentication

Protect incoming MCP requests with a Bearer token:

```json
{
    "server_auth": ["username", "password"]
}
```

Or via environment variable:

```
OPENBB_MCP_SERVER_AUTH='["username", "password"]'
```

Clients must include `Authorization: Bearer <base64(username:password)>` in
their requests. The token is base64-encoded `username:password`.

### Client-Side Authentication

Authenticate outbound requests to downstream services:

```json
{
    "client_auth": ["api_user", "api_key"]
}
```

Or via environment variable:

```
OPENBB_MCP_CLIENT_AUTH='["api_user", "api_key"]'
```

This passes `auth=(user, pass)` to the httpx client used for internal requests.

### Programmatic Authentication

When using the server as a library, pass a custom `AuthProvider` to
`create_mcp_server()`:

```python
from openbb_mcp_server.app.app import create_mcp_server
from openbb_mcp_server.models.settings import MCPSettings

settings = MCPSettings()
mcp = create_mcp_server(settings, my_fastapi_app, auth=my_auth_provider)
```

---

## Tool Discovery

When `enable_tool_discovery` is `true` (the default), five admin tools are
available to the agent:

| Tool | Description |
|---|---|
| `available_categories` | Lists all tool categories with tool counts |
| `available_tools` | Lists tools in a specific category with active state and short descriptions |
| `activate_tools` | Enables tools by name for this session |
| `deactivate_tools` | Disables tools by name for this session |
| `activate_category` | Bulk-activates all tools in a category (or subcategory) for this session |

All visibility changes are **per-session** — each connected client maintains its
own active toolset, so the server is safe for multi-user deployments.

### Controlling Active Tools on Startup

Use `default_tool_categories` to control which categories are active initially:

```
# Only equity and economy tools active on start
openbb-mcp --default-categories equity,economy

# All admin tools active (for exploration)
openbb-mcp --default-categories admin
```

The agent can then use `available_categories` and `activate_tools` (or
`activate_category` for bulk activation) to dynamically enable additional
tools as needed.

### Restricting Available Categories

Use `allowed_tool_categories` to permanently hide categories:

```
openbb-mcp --allowed-categories equity,economy,crypto
```

Categories not in this list cannot be activated even via discovery tools.

### Disabling Discovery

```
openbb-mcp --no-tool-discovery
```

All tools in `default_tool_categories` are active and the admin tools are
not registered.

---

## Tool Naming Convention

Tools are named from their API route path after stripping the API prefix:

| Route Path | Tool Name |
|---|---|
| `/equity/price/historical` | `equity_price_historical` |
| `/economy/cpi` | `economy_cpi` |
| `/my_app/process` | `my_app_process` |

The first path segment is the **category**, the last segment is the **tool
name**, and segments in between form the **subcategory**. When there is no
subcategory, it defaults to `"general"`.

---

## Prompt System

The server supports four layers of prompts, all accessible via the
`list_prompts` and `execute_prompt` tools.

### 1. System Prompt (tag: `system`)

A plain text file loaded once at startup. Also exposed as
`resource://system_prompt`.

```
openbb-mcp --system-prompt /path/to/system_prompt.txt
```

### 2. Server Prompts JSON (tag: `server`)

A JSON file defining reusable prompts with optional arguments:

```json
[
    {
        "name": "analyze_stock",
        "description": "Framework for analyzing a stock.",
        "content": "Analyze {symbol} focusing on {aspect}.",
        "arguments": [
            {
                "name": "symbol",
                "type": "str",
                "description": "Ticker symbol"
            },
            {
                "name": "aspect",
                "type": "str",
                "default": "fundamentals",
                "description": "Analysis focus area"
            }
        ],
        "tags": ["analysis"]
    }
]
```

Argument types: `str`, `int`, `float`, `bool`, `list`, `dict`, `any`

Arguments with a `default` value are optional; those without are required.

```
openbb-mcp --server-prompts /path/to/prompts.json
```

### 3. Inline Prompts (tag: route-specific)

Define prompts directly on FastAPI routes via `openapi_extra`:

```python
@router.command(
    methods=["GET"],
    openapi_extra={
        "mcp_config": {
            "prompts": [
                {
                    "name": "usage_guide",
                    "description": "How to use this endpoint.",
                    "content": "To analyze {symbol}, call this endpoint with..."
                }
            ]
        }
    },
)
async def my_endpoint(symbol: str) -> OBBject:
    ...
```

### 4. Bundled Skills (Resources)

Skill guides are exposed as MCP resources discoverable via `list_resources()`.
Each skill is accessible at a `skill://<name>/SKILL.md` URI.

```
# Discover available skills
list_resources()  # returns skill://develop_extension/SKILL.md, etc.

# Read a specific skill
read_resource("skill://configure_mcp_server/SKILL.md")
```

Custom skills directory:

```
OPENBB_MCP_DEFAULT_SKILLS_DIR=/path/to/my/skills
```

Set to empty string to disable bundled skills:

```
OPENBB_MCP_DEFAULT_SKILLS_DIR=""
```

### Skills Reload

Enable hot-reload of skill files without restarting the server (useful during development):

```json
{
    "skills_reload": true
}
```

Or via environment variable:

```
OPENBB_MCP_SKILLS_RELOAD=true
```

### Vendor Skills Providers

Load skill directories from well-known vendor locations (e.g. `~/.claude/skills/`).
Sets the `skills_providers` list in `mcp_settings.json`:

```json
{
    "skills_providers": ["claude", "cursor"]
}
```

Or via environment variable (comma-separated):

```
OPENBB_MCP_SKILLS_PROVIDERS="claude,cursor"
```

Supported provider names:

| Name | Default Directory |
|---|---|
| `claude` | `~/.claude/skills/` |
| `cursor` | `~/.cursor/skills/` |
| `vscode` / `copilot` | `~/.copilot/skills/` |
| `codex` | `/etc/codex/skills/` + `~/.codex/skills/` |
| `gemini` | `~/.gemini/skills/` |
| `goose` | `~/.config/agents/skills/` |
| `opencode` | `~/.config/opencode/skills/` |

---

## Inline MCP Configuration (MCPConfigModel)

Control how individual routes appear in the MCP server via `openapi_extra`:

```python
@app.get(
    "/my_endpoint",
    openapi_extra={
        "mcp_config": {
            "expose": True,
            "mcp_type": "tool",
            "methods": ["GET"],
            "exclude_args": ["internal_param"],
            "prompts": []
        }
    },
)
```

### MCPConfigModel Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `expose` | `bool \| None` | `None` | Set `false` to hide route from MCP |
| `mcp_type` | `str \| None` | `None` | `"tool"`, `"resource"`, or `"resource_template"` |
| `methods` | `list[str] \| None` | `None` | HTTP methods to expose |
| `exclude_args` | `list[str] \| None` | `None` | Arguments to hide from the tool schema |
| `prompts` | `list[dict]` | `[]` | Inline prompt definitions |

---

## Client Configuration Examples

### Claude Desktop (stdio transport)

In Claude Desktop's MCP config file:

```json
{
    "mcpServers": {
        "openbb-mcp": {
            "command": "uvx",
            "args": [
                "--from", "openbb-mcp-server",
                "--with", "openbb",
                "openbb-mcp",
                "--transport", "stdio"
            ]
        }
    }
}
```

For a custom app:

```json
{
    "mcpServers": {
        "openbb-mcp": {
            "command": "uvx",
            "args": [
                "--from", "openbb-mcp-server",
                "openbb-mcp",
                "--app", "./my_app.py",
                "--transport", "stdio"
            ]
        }
    }
}
```

### Cursor (streamable-http)

1. Start the server: `openbb-mcp`
2. In Cursor's `mcp.json`:

```json
{
    "mcpServers": {
        "openbb-mcp": {
            "url": "http://localhost:8001/mcp/"
        }
    }
}
```

### VS Code (streamable-http)

1. Enable MCP in VS Code settings (Settings → Chat → MCP)
2. Start the server: `openbb-mcp`
3. Open Command Palette → "MCP: Add Server" → HTTP
4. Enter URL: `http://127.0.0.1:8001/mcp`

For the Cline VS Code extension, use `--transport sse`:

```
openbb-mcp --transport sse
```

### With Authentication

Start with server auth enabled:

```
openbb-mcp --host 0.0.0.0 --port 8001
```

With `mcp_settings.json`:

```json
{
    "server_auth": ["admin", "secretpass"]
}
```

Clients include the Bearer token in their configuration:

```json
{
    "mcpServers": {
        "openbb-mcp": {
            "url": "http://localhost:8001/mcp/",
            "headers": {
                "Authorization": "Bearer YWRtaW46c2VjcmV0cGFzcw=="
            }
        }
    }
}
```

The token value is `base64("admin:secretpass")`.

---

## Advanced Configuration

### Lists and Dicts in Environment Variables

Lists can be passed as comma-separated strings:

```
OPENBB_MCP_DEFAULT_TOOL_CATEGORIES="equity,economy,crypto"
OPENBB_MCP_ALLOWED_TOOL_CATEGORIES="equity,economy"
```

Dicts and tuples must be JSON-encoded strings:

```
OPENBB_MCP_SERVER_AUTH='["user", "pass"]'
OPENBB_MCP_UVICORN_CONFIG='{"host": "0.0.0.0", "port": 8001, "log_level": "info"}'
OPENBB_MCP_HTTPX_CLIENT_KWARGS='{"timeout": 30, "verify": false}'
```

### SSL / HTTPS

Pass SSL config via Uvicorn:

```
openbb-mcp --ssl-keyfile /path/to/key.pem --ssl-certfile /path/to/cert.pem
```

Or in the config file:

```json
{
    "uvicorn_config": {
        "host": "0.0.0.0",
        "port": 443,
        "ssl_keyfile": "/path/to/key.pem",
        "ssl_certfile": "/path/to/cert.pem"
    }
}
```

### Using as a Library

```python
import asyncio
from fastapi import FastAPI
from openbb_mcp_server.app.app import create_mcp_server
from openbb_mcp_server.models.settings import MCPSettings

app = FastAPI()

@app.get("/hello")
async def hello():
    return "Hello World"

settings = MCPSettings(
    name="My Custom MCP",
    default_tool_categories=["all"],
    enable_tool_discovery=True,
)

mcp = create_mcp_server(settings, app)
mcp.run(transport="streamable-http")
```

---

## Workflow Summary

To configure and deploy an OpenBB MCP server:

1. **Install**: `pip install openbb-mcp-server` (plus any desired OpenBB extensions).
2. **Configure**: Create `~/.openbb_platform/mcp_settings.json` with desired settings.
3. **Add prompts**: Write a system prompt file and/or server prompts JSON.
4. **Start**: Run `openbb-mcp` with appropriate CLI flags.
5. **Connect**: Configure your MCP client (Claude Desktop, Cursor, VS Code) with the server URL or stdio command.
6. **Discover**: Use `available_categories`, `activate_tools`, and `activate_category` to find and enable tools.
7. **Iterate**: Adjust settings, add inline `mcp_config` to routes, add skill files.
