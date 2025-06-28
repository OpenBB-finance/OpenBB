# OpenBB MCP Server

Model Context Protocol (MCP) server extension for OpenBB Platform. This extension enables LLM agents to interact with OpenBB Platform's REST API endpoints through the MCP protocol.

The server provides management tools that allow agents to explore different options and dynamically adjust their active toolset. This prevents agents from being overwhelmed with too many tools while allowing them to discover and activate only the tools they need for specific tasks.

Using these dynamic tool discovery, has one major drawback, it makes the server a single-user server. The tool updates are global, so if one user updates a tool, it will be updated for all users. If you plan to server multiple users, you should disable tool discovery, and instead use the `allowed_tool_categories` and `default_tool_categories` settings to control the tools that are available to the users.

## Installation

```bash
pip install openbb-mcp-server
```

## Usage

Start the OpenBB MCP server with default settings:

```bash
openbb-mcp
```

### Command Line Options

- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to listen on (default: 8001)
- `--allowed-categories`: Comma-separated list of allowed tool categories
- `--default-categories`: Comma-separated list of categories enabled at startup (default: all)
- `--transport`: Transport protocol (default: streamable-http)
- `--no-tool-discovery`: Disable tool discovery for multi-client deployments

### Examples

```bash
# Start with default settings
openbb-mcp

# Start with specific categories and custom host/port
openbb-mcp --default-categories equity,news --host 0.0.0.0 --port 8080

# Start with allowed categories restriction
openbb-mcp --allowed-categories equity,crypto,news

# Disable tool discovery for multi-client usage
openbb-mcp --no-tool-discovery
```

## Configuration

The server can be configured through multiple methods:

### 1. Configuration File (Recommended)

The server automatically creates and uses `~/.openbb_platform/mcp_settings.json`:

```json
{
  "name": "OpenBB MCP",
  "description": "All OpenBB REST endpoints exposed as MCP tools...",
  "default_tool_categories": ["all"],
  "allowed_tool_categories": null,
  "enable_tool_discovery": true,
  "describe_responses": true
}
```

### 2. Environment Variables

Override settings using environment variables:
- `OPENBB_MCP_NAME`: Server name
- `OPENBB_MCP_DESCRIPTION`: Server description  
- `OPENBB_MCP_DEFAULT_TOOL_CATEGORIES`: Comma-separated list of default categories
- `OPENBB_MCP_ALLOWED_TOOL_CATEGORIES`: Comma-separated list of allowed categories
- `OPENBB_MCP_ENABLE_TOOL_DISCOVERY`: true/false - Enable tool discovery features
- `OPENBB_MCP_DESCRIBE_ALL_RESPONSES`: true/false - Include response details in descriptions
- `OPENBB_MCP_DESCRIBE_FULL_RESPONSE_SCHEMA`: true/false - Include full response schemas

### 3. Command Line Arguments

Command line arguments override both configuration file and environment variables.

## Settings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| name | string | "OpenBB MCP" | Server name displayed to MCP clients |
| description | string | "All OpenBB REST endpoints..." | Server description |
| default_tool_categories | list[string] | ["all"] | Categories enabled at startup. Use "all" to enable all categories, or specify individual categories |
| allowed_tool_categories | list[string] | null | If set, restricts available categories to this list |
| enable_tool_discovery | boolean | true | Enable discovery and management tools |
| describe_responses | boolean | true | Include response information in tool descriptions |

## Tool Categories

The server organizes OpenBB tools into categories based on the REST API structure:

- **`equity`** - Stock data, fundamentals, price history, estimates
- **`crypto`** - Cryptocurrency data and analysis  
- **`economy`** - Economic indicators, GDP, employment data
- **`news`** - Financial news from various sources
- **`fixedincome`** - Bond data, rates, government securities
- **`derivatives`** - Options and futures data
- **`etf`** - ETF information and holdings
- **`currency`** - Foreign exchange data
- **`commodity`** - Commodity prices and data
- **`index`** - Market indices data
- **`regulators`** - SEC, CFTC regulatory data

Each category contains subcategories that group related functionality (e.g., `equity_price`, `equity_fundamental`, etc.).

## Tool Discovery

When `enable_tool_discovery` is enabled (default), the server provides management tools that allow agents to:

- Discover available tool categories and subcategories
- See tool counts and descriptions before activating
- Enable/disable specific tools dynamically during a session
- Start with minimal tools and progressively add more as needed

To take full advantage of minimal startup tools, you should set the `--default-categories` argument to `admin` this will enable only the discovery tools at startup.

For multi-client deployments or scenarios where you want a fixed toolset, disable tool discovery with `--no-tool-discovery`.