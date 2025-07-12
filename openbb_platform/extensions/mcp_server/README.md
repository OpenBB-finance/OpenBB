# OpenBB MCP Server

Model Context Protocol (MCP) server extension for OpenBB Platform. This extension enables LLM agents to interact with OpenBB Platform's REST API endpoints through the MCP protocol.

In addition, the server provides discovery tools that allow agents to explore different options and dynamically adjust their active toolset. This prevents agents from being overwhelmed with too many tools while allowing them to discover and activate only the tools they need for specific tasks.

Using these dynamic tool discovery, has one major drawback, it makes the server a single-user server. The tool updates are global, so if one user updates a tool, it will be updated for all users. If you plan to server multiple users, you should disable tool discovery, and instead use the `allowed_tool_categories` and `default_tool_categories` settings to control the tools that are available to the users.

## Installation & Usage

```bash
pip install openbb-mcp-server
```

Start the OpenBB MCP server with default settings:

```bash
openbb-mcp
```

Or use the `uvx` command:

```bash
uvx --from openbb-mcp-server --with openbb openbb-mcp
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

#### Claude Desktop:

To connect the OpenBB MCP server with Claude Desktop, you need to configure it as a custom tool server. Here are the steps:

1.  Locate the settings or configuration file for Claude Desktop where you can define custom MCP servers.
2.  Add the following entry to your `mcpServers` configuration. This will configure Claude Desktop to launch the OpenBB MCP server automatically using `stdio` for communication.

```json
{
  "mcpServers": {
    "openbb-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "openbb-mcp-server",
        "--with",
        "openbb",
        "openbb-mcp",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

3.  Ensure that `uvx`, is installed and available in your system's PATH. If not, follow the installation instructions.
4.  Restart Claude Desktop to apply the changes. You should now see "openbb-mcp" as an available tool source.

#### Cursor:

To use OpenBB tools within Cursor, you first need to run the MCP server and then tell Cursor how to connect to it.

**Step 1: Run the OpenBB MCP Server**

Open your terminal and start the server. You can use the default settings or customize it.

For a default setup, run:
```bash
openbb-mcp
```
The server will start on `http://127.0.0.1:8001`.

**Step 2: Configure Cursor**

Add the following configuration to the `mcpServers` object in your `mcp.json` file. If the `mcpServers` object doesn't exist, you can add it.

```json
{
  "mcpServers": {
    "openbb-mcp": {
      "url": "http://localhost:8001/mcp/"
    }
  }
}
```


#### VS Code

**Step 1: Enable MCP in VS Code Settings**

Enter `shift + command + p` and open "Preferences: Open User Settings"

Search for "mcp", and the item should show up under "Chat". Check the box to enable MCP server integrations.

<img width="1278" height="411" alt="vs-code-mcp-enable" src="https://github.com/user-attachments/assets/5ace29de-e59c-45c3-b751-c6d92614e0ee" />


**Step 2: Run the OpenBB MCP Server**

Open your terminal and start the server. You can use the default settings or customize it.

For a default setup, run:
```bash
openbb-mcp
```
The server will start on `http://127.0.0.1:8001`.

**Step 3: Add Server as HTTP**

Enter `shift + command + p` and select "MCP: Add Server".

<img width="595" height="412" alt="vs-code-mcp-commands" src="https://github.com/user-attachments/assets/9b13a5b6-ec20-43e2-9aae-7982e9fdcae6" />

Press enter and then select HTTP.

<img width="594" height="174" alt="vs-code-mcp-add-http" src="https://github.com/user-attachments/assets/d2a06e4b-404a-4317-ad2c-241c1ac5e04b" />

Copy the URL from the console of the running server, and enter it

```sh
INFO     Starting MCP server 'OpenBB MCP' with transport 'streamable-http' on http://127.0.0.1:8001/mcp
```

Give it a name, and add it either as global or to a workspace. The end result will create a `mcp.json` VS Code configuration file for the chosen domain.

<img width="402" height="195" alt="vs-code-mcp-json" src="https://github.com/user-attachments/assets/fdea335b-0523-4103-be3e-b5d9675c25b3" />

The tools can now be added as context to the chat.

<img width="601" height="442" alt="vs-code-mcp-tools" src="https://github.com/user-attachments/assets/06c39248-aedd-4f53-9560-6dfbae1efaf8" />


**Note**: When adding to the Cline extension, set `--transport sse` when starting the server.


## Configuration

The server can be configured through multiple methods:

> **Note:** For some data providers you need to set your API key in the `~/.openbb_platform/user_settings.json` file.

### 1. Configuration File (Recommended)

The server automatically creates and uses `~/.openbb_platform/mcp_settings.json`:

```json
{
  "name": "OpenBB MCP",
  "description": "All OpenBB REST endpoints exposed as MCP tools...",
  "default_tool_categories": ["all"],
  "allowed_tool_categories": null,
  "enable_tool_discovery": true,
  "describe_responses": false
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
| describe_responses | boolean | false | Include response information in tool descriptions |

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

When `enable_tool_discovery` is enabled (default), the server provides discovery tools that allow agents to:

- Discover available tool categories and subcategories
- See tool counts and descriptions before activating
- Enable/disable specific tools dynamically during a session
- Start with minimal tools and progressively add more as needed

To take full advantage of minimal startup tools, you should set the `--default-categories` argument to `admin` this will enable only the discovery tools at startup.

For multi-client deployments or scenarios where you want a fixed toolset, disable tool discovery with `--no-tool-discovery`.
