# OpenBB MCP Server

Model Context Protocol (MCP) server extension for OpenBB Platform. This extension enables LLM agents to interact with OpenBB Platform's REST API endpoints through the MCP protocol.

In addition to the REST API endpoints, the server provides management endpoints that allow agents to explore different options and dynamically adjust their active toolset. This prevents agents from being overwhelmed with too many tools while allowing them to discover and activate only the tools they need for specific tasks.

## Installation

```bash
pip install openbb-mcp-server
```

## Usage

Start the MCP server:

```bash
openbb-mcp [options]
```

Options:
- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to listen on (default: 8001)
- `--categories`: Initial tool categories to enable (comma-separated)
- `--log-level`: Logging level (default: info)

## Management Endpoints

The server provides several endpoints that allow agents to explore and manage their toolset:

### Tool Category Management
- **GET `/mcp/available_tool_categories`** - Get all available tool categories and currently active ones
- **POST `/mcp/activate_tool_categories`** - Activate specific tool categories (makes their tools available for selection)

### Tool Management  
- **GET `/mcp/available_tools`** - Get available tools for active categories and currently active tools
- **POST `/mcp/activate_tools`** - Activate specific tools (these become available to the LLM)

### Example Workflow
1. **Explore categories**: Agent calls `available_tool_categories` to see what's available
2. **Activate categories**: Agent activates relevant categories with `activate_tool_categories` 
3. **Explore tools**: Agent calls `available_tools` to see tools in active categories
4. **Activate tools**: Agent selects specific tools with `activate_tools`

This allows agents to start with a minimal toolset and progressively discover and activate only the tools they need.

## Configuration

The server can be configured through:

1. **System Settings (recommended)**:
   Add an "mcp_settings" section to your `~/.openbb_platform/system_settings.json`:

```json
{
  "mcp_settings": {
    "name": "OpenBB MCP",
    "description": "OpenBB Platform MCP Server",
    "default_tool_categories": ["equity", "news"],
    "allowed_tool_categories": null,
    "require_valid_credentials": true,
    "allowed_providers": null,
    "initial_tools": null,
    "allowed_tools": null,
    "describe_all_responses": false,
    "describe_full_response_schema": false
  }
}
```

2. **Command Line Arguments**:
   Command line arguments override system settings for host, port, categories, and log level.

## Settings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| name | string | "OpenBB MCP" | Server name |
| description | string | "OpenBB Platform MCP Server" | Server description |
| default_tool_categories | list[string] | ["equity"] | Default active tool categories on startup |
| allowed_tool_categories | list[string] | null | If set, restricts available tool categories to this list |
| require_valid_credentials | boolean | true | Only allow providers with valid credentials |
| allowed_providers | list[string] | null | If set, restricts available providers to this list |
| initial_tools | list[string] | null | Initial tools to activate. If None, only required tools will be active |
| allowed_tools | list[string] | null | If set, restricts available tools to this list |
| describe_all_responses | boolean | false | Include all possible response types in tool descriptions |
| describe_full_response_schema | boolean | false | Include full response schema in tool descriptions |

## Required Tools

The following tools are always available and cannot be disabled:
- `get_available_tool_categories`
- `activate_tool_categories`
- `get_available_tools`
- `activate_tools`

## Tool Categories

The server organizes OpenBB tools into categories such as:
- `equity` - Stock data and analysis
- `news` - Financial news
- `crypto` - Cryptocurrency data
- `economy` - Economic indicators
- And more...

## Provider Management

The server can filter tools based on data providers:
- Set `allowed_providers` to restrict which providers are available
- Set `require_valid_credentials` to only show providers with valid API keys
- Configure provider credentials through OpenBB Platform's standard settings

## Example Usage

```bash
# Start with default settings
openbb-mcp

# Start with specific categories and debug logging
openbb-mcp --categories equity,news --log-level debug

# Start on custom host and port
openbb-mcp --host 0.0.0.0 --port 8080
```

## Development

1. Clone the repository
2. Install dependencies: `uv install`
3. Run tests: `uv run pytest`
4. Start development server: `uv run python openbb_platform/extensions/mcp-server/openbb_mcp_server/main.py`

## Future MCP Features

The Model Context Protocol supports additional features that could be valuable:
- **Resources** - Expose datasets, files, or other resources that tools can reference
- **Prompt Templates** - Predefined prompts that help agents use tools more effectively
- **Sampling** - Allow the server to generate content using LLMs

These features could enhance the agent experience and provide more sophisticated interactions with financial data.