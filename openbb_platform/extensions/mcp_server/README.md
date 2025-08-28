# OpenBB MCP Server

This extension enables LLM agents to interact with OpenBB Platform's REST API endpoints through the MCP protocol.

The server provides discovery tools that allow agents to explore different options and dynamically adjust their active toolset.
This prevents agents from being overwhelmed with too many tools while allowing them to discover and activate only the tools they need for specific tasks.

Using dynamic tool discovery has one major drawback, it makes the server a single-user server.
The tool updates are global, so if one user updates a tool, it will be updated for all users.

If you plan to serve multiple users, you should disable tool discovery,
and instead use the `allowed_tool_categories` and `default_tool_categories` settings to control the tools that are available to the users.

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

Enter `openbb-mcp --help` to see the docstring from the command line.

```sh
--help
    Show this help message and exit.

--app <app_path>
    The path to the FastAPI app instance. This can be in the format
    'module.path:app_instance' or a file path 'path/to/app.py'.
    If not provided, the server will run with the default built-in app.

--name <name>
    The name of the FastAPI app instance or factory function in the app file.
    Defaults to 'app'.

--factory
    If set, the app is treated as a factory function that will be called
    to create the FastAPI app instance.

--host <host>
    The host to bind the server to. Defaults to '127.0.0.1'.
    This is a uvicorn argument.

--port <port>
    The port to bind the server to. Defaults to 8000.
    This is a uvicorn argument.

--transport <transport>
    The transport mechanism to use for the MCP server.
    Defaults to 'streamable-http'.

--allowed-categories <categories>
    A comma-separated list of tool categories to allow.
    If not provided, all categories are allowed.

--default-categories <categories>
    A comma-separated list of tool categories to be enabled by default.
    Defaults to 'all'.

--no-tool-discovery
    If set, tool discovery will be disabled.

--system-prompt <path>
    Path to a TXT file with the system prompt.

--server-prompts <path>
    Path to a JSON file with a list of server prompts.
```

#### All other arguments will be passed to `uvicorn.run`.


## Configuration

The server can be configured through multiple methods, with settings applied in the following order of precedence:

1.  **Command Line Arguments**: Highest priority, overriding all other methods.
2.  **Environment Variables**: Each setting can be controlled by an environment variable, which will override the configuration file.
3.  **Configuration File**: A JSON file at `~/.openbb_platform/mcp_settings.json` provides the base configuration.
  - If the cnofiguration file does not exist, one will be populated with the defaults.

> **Note:** For some data providers you need to set your API key in the `~/.openbb_platform/user_settings.json` file.

### Authentication

The MCP server supports client-side and server-side authentication to secure your endpoints.

#### Server-Side Authentication

Server-side authentication requires incoming requests to provide credentials. This is configured using the `server_auth` setting, which accepts a tuple of `(username, password)`.

When `server_auth` is enabled, clients must include an `Authorization` header with a `Bearer` token. The token should be a Base64-encoded string of `username:password`.

**Example: Environment Variable**

```env
OPENBB_MCP_SERVER_AUTH='["myuser", "mypass"]'
```

**Example: `mcp_settings.json`**

```json
{
  "server_auth": ["myuser", "mypass"]
}
```

#### Client-Side Authentication

Client-side authentication configures the MCP server to use credentials when making downstream requests. This is useful when the server needs to authenticate with other services.

**Example: Environment Variable**

```env
OPENBB_MCP_CLIENT_AUTH='["client_user", "client_pass"]'
```

**Example: `mcp_settings.json`**

```json
{
  "client_auth": ["client_user", "client_pass"]
}
```

#### Programmatic Authentication

For advanced use cases, you can pass a pre-configured authentication object directly to the `create_mcp_server` function using the `auth` parameter. This allows you to implement custom authentication logic or use third-party authentication providers.

```python
from fastmcp.server.auth.providers import BearerProvider
from openbb_mcp_server.app import create_mcp_server

# Create a custom auth provider
custom_auth = BearerProvider(...)

# Pass it to the server
mcp_server = create_mcp_server(settings, fastapi_app, auth=custom_auth)
```

### Advanced Configuration: Lists and Dictionaries

For settings that accept a list or a dictionary, you have two flexible formats for defining them in both command-line arguments and environment variables.

#### 1. Comma-Separated Strings

This is a simple and readable way to define lists and simple dictionaries.

-   **Lists**: Provide a string of comma-separated values.
    -   Example: `equity,news,crypto`
-   **Dictionaries**: Provide a string of comma-separated `key:value` pairs.
    -   Example: `host:0.0.0.0,port:9000`

#### 2. JSON-Encoded Strings

For more complex data structures, or to ensure precise type handling (e.g., for numbers and booleans), you can use a JSON-encoded string.

-   **Lists**: A standard JSON array.
    -   Example: `'["equity", "news", "crypto"]'`
-   **Dictionaries**: A standard JSON object.
    -   Example: `'{"host": "0.0.0.0", "port": 9000}'`

**Important Note on Quoting**: When passing JSON-encoded strings on the command line, it is highly recommended to wrap the entire string in **single quotes (`'`)**. This prevents your shell from interpreting the double quotes (`"`) inside the JSON string, which can lead to parsing errors.

#### Practical Examples

Here’s how you can apply these formats in practice:

**Command-Line Arguments:**

```sh
# List with comma-separated values
openbb-mcp --default-categories equity,news

# List with a JSON-encoded string (note the single quotes)
openbb-mcp --default-categories '["equity", "news"]'

# Dictionary with comma-separated key:value pairs
openbb-mcp --uvicorn-config "host:0.0.0.0,port:9000"

# Dictionary with a JSON-encoded string (note the single quotes)
openbb-mcp --uvicorn-config '{"host": "0.0.0.0", "port": 9000, "env_file": "./path_to/.env"}'
```

**Environment Variables (in a `.env` file):**

```env
# List with comma-separated values
OPENBB_MCP_DEFAULT_TOOL_CATEGORIES="equity,news"

# List with a JSON-encoded string
OPENBB_MCP_DEFAULT_TOOL_CATEGORIES='["equity", "news"]'

# Dictionary with comma-separated key:value pairs
OPENBB_MCP_UVICORN_CONFIG="host:0.0.0.0,port:9000"

# Dictionary with a JSON-encoded string
OPENBB_MCP_UVICORN_CONFIG='{"host": "0.0.0.0", "port": 9000, "env_file": "./path_to/.env"}'
```

## Settings Reference

All settings in the `MCPSettings` model can be configured via the `mcp_settings.json` file or as environment variables.

| Setting | Environment Variable | Type | Default | Description |
|---|---|---|---|---|
| `api_prefix` | `OPENBB_MCP_API_PREFIX` | string | `None` | Overrides the API prefix from SystemService. |
| `name` | `OPENBB_MCP_NAME` | string | `"OpenBB MCP"` | Server name. |
| `description` | `OPENBB_MCP_DESCRIPTION` | string | | Server description. |
| `version` | `OPENBB_MCP_VERSION` | string | `None` | Server version. |
| `default_tool_categories` | `OPENBB_MCP_DEFAULT_TOOL_CATEGORIES` | list[string] | `["all"]` | Default active tool categories on startup. |
| `allowed_tool_categories` | `OPENBB_MCP_ALLOWED_TOOL_CATEGORIES` | list[string] | `None` | Restricts available tool categories to this list. |
| `enable_tool_discovery` | `OPENBB_MCP_ENABLE_TOOL_DISCOVERY` | boolean | `True` | Enable tool discovery. |
| `describe_responses` | `OPENBB_MCP_DESCRIBE_RESPONSES` | boolean | `False` | Include response types in tool descriptions. |
| `system_prompt_file` | `OPENBB_MCP_SYSTEM_PROMPT_FILE` | string | `None` | Path to a text file for the system prompt. |
| `server_prompts_file` | `OPENBB_MCP_SERVER_PROMPTS_FILE` | string | `None` | Path to a JSON file with a list of server prompt definitions. |
| `cache_expiration_seconds` | `OPENBB_MCP_CACHE_EXPIRATION_SECONDS` | float | `None` | Cache expiration time in seconds. `0` to disable. |
| `on_duplicate_tools` | `OPENBB_MCP_ON_DUPLICATE_TOOLS` | string | `None` | Behavior for duplicate tools (`warn`, `error`, `replace`, `ignore`). |
| `on_duplicate_resources` | `OPENBB_MCP_ON_DUPLICATE_RESOURCES` | string | `None` | Behavior for duplicate resources. |
| `on_duplicate_prompts` | `OPENBB_MCP_ON_DUPLICATE_PROMPTS` | string | `None` | Behavior for duplicate prompts. |
| `resource_prefix_format` | `OPENBB_MCP_RESOURCE_PREFIX_FORMAT` | string | `None` | Format for resource URI prefixes (`protocol` or `path`). |
| `mask_error_details` | `OPENBB_MCP_MASK_ERROR_DETAILS` | boolean | `None` | Mask error details from user functions. |
| `dependencies` | `OPENBB_MCP_DEPENDENCIES` | list[string] | `None` | List of dependencies to install. |
| `include_tags` | `OPENBB_MCP_INCLUDE_TAGS` | set[string] | `None` | Only expose components with these tags. |
| `exclude_tags` | `OPENBB_MCP_EXCLUDE_TAGS` | set[string] | `None` | Exclude components with these tags. |
| `module_exclusion_map` | `OPENBB_MCP_MODULE_EXCLUSION_MAP` | dict[str, str] | `None` | Map API tags to Python module names for exclusion. |
| `uvicorn_config` | `OPENBB_MCP_UVICORN_CONFIG` | dict | `{"host": "127.0.0.1", "port": "8001"}` | Configuration for the Uvicorn server. |
| `httpx_client_kwargs` | `OPENBB_MCP_HTTPX_CLIENT_KWARGS` | dict | `{}` | Configuration for the async httpx client. |
| `client_auth` | `OPENBB_MCP_CLIENT_AUTH` | tuple[string, string] | `None` | `(username, password)` for client-side basic authentication (passed-through to HTTPX). |
| `server_auth` | `OPENBB_MCP_SERVER_AUTH` | tuple[string, string] | `None` | `(username, password)` for server-side basic authentication. |

> **Note:** Runtime argument keys, in general, "-" and "_" are interchangeable. Nested uvicorn arguments should use `_`.

## Tool Categories

The server organizes OpenBB tools into categories based on the included API Routers (paths).
Categories depend on the installed extensions, but will be the first path in the API after the given prefix.

For example:

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

### Root Tools

An additional set of tools are tagged as "admin", or "prompt".

- available_categories

- available_tools: List all tools by category.
  - `category`: Category of tool to list.
  - `subcategory`: Optional subcategory. Use 'general' for tools directly under the category.

- activate_tools: Activate a tool for use.
  - `tool_names`: Names of tools to activate. Comma-separated string for multiple.

- deactivate_tools: Deactivate a tool after use.
  - `tool_names`: Names of tools to deactivate. Comma-separated string for multiple.

- list_prompts: Lists all available prompts in the server.

- execute_prompt: Execute a prompt with arguments, if any.
  - `prompt_name`: Name of the prompt to execute.
  - `arguments`: Dictionary of argument:value for the prompt.

## Tool Discovery

When `enable_tool_discovery` is enabled (default), the server provides discovery tools that allow agents to:

- Discover available tool categories and subcategories
- See tool counts and descriptions before activating
- Enable/disable specific tools dynamically during a session
- Start with minimal tools and progressively add more as needed

To take full advantage of minimal startup tools, you should set the `--default-categories` argument to `admin`. This will enable only the discovery tools at startup.

For multi-client deployments or scenarios where you want a fixed toolset, disable tool discovery with `--no-tool-discovery`.

## System Prompt

A system prompt file can be added on initialization, or defined in the configuration file, or as an environment variable.
It should be a valid, relative or absolute, path to a `.txt` file.

The system prompt is made available as a resource, `resource://system_prompt`, and is discoverable from the, `list_prompts`, tool.

Clients will not automatically use the system prompt, instruct them to use it as part of their onboarding and orientation.

## Server Prompts

A system prompt file can be added on initialization, or defined in the configuration file, or as an environment variable.
It should be a valid, relative or absolute, path to a `.json` file with a list of prompt definitions.

Each entry in the JSON file is a dictionary with the following properties:

- **`name`**: Name of the prompt.
- **`description`**: A brief description of the prompt.
- **`content`**: The content for rendering the prompt.
- **`arguments`**: Optional list of arguments.
  - **`name`**: Name of the argument.
  - **`type`**: Simple Python type as a string - i.e, "int".
  - **`default`**: Supplying a default value makes the parameter Optional.
  - **`description`**: Description of the parameter. Supply need-to-know details for the LLM.
- **`tags`**: List of tags to apply to the argument.

Prompts here should provide the LLM a clear path for executing a workflow combining multiple tools or steps, for example:

```json
[
    {
      "name": "equity_analysis",
      "description": "Perform a comprehensive equity analysis using multiple data sources and metrics",
      "content": "Conduct a comprehensive analysis of {symbol} for {analysis_period}. Follow this workflow:\n1. First, get basic stock quote and recent price performance using equity_price_performance.\n2. Retrieve fundamental data including financial statements, ratios, and key metrics using [equity_fundamental_ratios, equity_fundamental_metrics, quity_fundamental_balance].\n3. Gather recent news and analyst estimates for the company using [news_company, equity_estiments_price_target].\n4. Compare valuation metrics with industry peers using equity_compare_peers.\n5. Summarize findings with investment recommendation.\n\nFocus areas: {focus_areas}\nRisk tolerance: {risk_tolerance}",
      "arguments": [
        {
          "name": "symbol",
          "type": "str",
          "description": "Stock ticker symbol to analyze (e.g., AAPL, TSLA)"
        },
        {
          "name": "analysis_period",
          "type": "str",
          "default": "last 12 months",
          "description": "Time period for the analysis"
        },
        {
          "name": "focus_areas",
          "type": "str",
          "default": "growth, profitability, valuation",
          "description": "Specific areas to focus on in the analysis"
        },
        {
          "name": "risk_tolerance",
          "type": "str",
          "default": "moderate",
          "description": "Risk tolerance level: conservative, moderate, or aggressive"
        }
      ],
      "tags": ["equity", "analysis", "comprehensive"]
    }
]
```

An invalid prompt definition, or prompt argument, will be logged to the console as an error.
The item will be ignored, and will not raise an error.

## Inline Prompts

Prompts can be added to an endpoint through the `openapi_extra` dictionary.

Adding prompts here will help the LLM use the endpoint for specific purposes, with less reasoning overhead.

Direct it to `execute_prompt`, or to make note that helpful prompts may be included in the tool's metadata.

The block below assumes `app` is an instance of `FastAPI`

```python
@app.get(
    "/economy/gdp",
    openapi_extra={
        "mcp_config": {
            "prompts": [
                {
                    "name": "gdp_summary_prompt",
                    "description": "Generate a brief summary of GDP for a country.",
                    "content": "Provide a concise summary of the GDP for {country} over the last {years} years.",
                    "arguments": [
                        {
                            "name": "years",
                            "type": "int",
                            "default": 5,
                            "description": "Number of years to summarize.",
                        }
                    ],
                    "tags": ["economy", "gdp", "summary"],
                },
                {
                    "name": "gdp_comparison_prompt",
                    "description": "Compare the GDP of two countries.",
                    "content": "Compare the GDP growth of {country1} and {country2}.",
                    "arguments": [
                        {
                            "name": "country1",
                            "type": "str",
                            "description": "First country for comparison.",
                        },
                        {
                            "name": "country2",
                            "type": "str",
                            "description": "Second country for comparison.",
                        },
                    ],
                    "tags": ["economy", "gdp", "comparison"],
                },
            ]
        }
    },
)
def get_gdp_data(country: str, period: Literal["annual", "quarterly"] = "annual"):
    """Get GDP data for a specific country."""
    return {"country": country, "period": period}
```

Along with being added to `list_prompts`, prompts will be included with the tool's metadata, returned by `list_tools`.

The discovery metadata for this tool would look like:

__Economy Tools:__

- __`economy_gdp`__: Get GDP data for a specific country.

  - __Associated Prompts:__

    - `gdp_summary_prompt`: Generate a brief summary of GDP for a country. (Arguments: `years`, `country`)
    - `gdp_comparison_prompt`: Compare the GDP of two countries. (Arguments: `country1`, `country2`)

Use a prompt with the `execute_prompt` tool:

```json
{
  "prompt_name": "gdp_summary_prompt",
  "arguments": {
    "years": 10,
    "country": "Japan"
  }
}
```

Which outputs:

```json
{
  "description": "Generate a brief summary of GDP for a country.",
  "messages": [
    {
      "role": "user",
      "content": {
        "type": "text",
        "text": "Use the tool, economy_gdp, to perform the following task.\n\nProvide a concise summary of the GDP for Japan over the last 10 years."
      }
    }
  ]
}
```

## Inline MCP Configuration

In addition to defining prompts, the `openapi_extra.mcp_config` dictionary allows for more granular control over how your FastAPI routes are exposed as MCP tools.
By using the `MCPConfigModel`, you can validate your configuration and access several powerful properties to customize tool behavior.

It can be imported with:

```
from openbb_mcp_server.models.mcp_config import MCPConfigModel
```

Including this configuration in the `openapi_extra` slot will override any automatically generated value.
You only need to enter the values that you wish to customize.

Below are the properties you can define within `mcp_config`:

-   **`expose`** (`Optional[bool]`): Set to `False` to completely hide a route from the MCP server. This is useful for internal or deprecated endpoints that should not be available as tools.

-   **`mcp_type`** (`Optional[MCPType]`): Classify the route as a specific MCP type. Valid options are `"tool"`, `"resource"`, or `"resource_template"`.

-   **`methods`** (`Optional[list[HTTPMethod]]`): Specify which HTTP methods to expose for a route that supports multiple methods (e.g., GET, POST). If omitted, all supported methods are exposed. Valid methods include `"GET"`, `"POST"`, `"PUT"`, `"PATCH"`, `"DELETE"`, `"HEAD"`, `"OPTIONS"`, and `*` (for all).

-   **`exclude_args`** (`Optional[list[str]]`): Provide a list of argument names to exclude from the tool’s signature. This is useful for filtering out parameters that are handled internally or are not relevant to the end-user.

- **`prompts`** (`Optional[list[dict[str, str]]]`): List of prompts specific to the endpoint. Keys for a prompt are:
  - **`name`**: Name of the prompt.
  - **`description`**: A brief description of the prompt.
  - **`content`**: The content for rendering the prompt. Endpoint parameters are inferred by placeholders.
  - **`arguments`**: Optional list of arguments. Items can be exclusive to the prompt, and not referenced in the endpoint.
    - **`name`**: Name of the argument.
    - **`type`**: Simple Python type as a string - i.e, "int".
    - **`default`**: Supplying a default value makes the parameter Optional.
    - **`description`**: Description of the parameter. Supply need-to-know details for the LLM.
  - **`tags`**: List of tags to apply to the argument.

### MCPConfigModel Validation

Values will be validated by the model before including in the server. Invalid configurations will be logged to the console as an error, and the inline definition will be ignored.

```console
ERROR    Invalid MCP config found in route, 'GET /equity/price'. Skipping tool customization because of validation error ->
          1 validation error for MCPConfigModel
          mcp_type
            Input should be 'tool', 'resource' or 'resource_template' [type=enum, input_value='some_setting', input_type=str]
              For further information visit https://errors.pydantic.dev/2.11/v/enum
```


### Example

Here is an example demonstrating how to use these properties to fine-tune a tool’s behavior:

```python
@app.get(
    "/some/route",
    openapi_extra={
        "mcp_config": {
            "expose": True,
            "mcp_type": "tool",
            "methods": ["GET"],
            "exclude_args": ["internal_param"],
            "prompts": [
                # ... prompt definitions ...
            ]
        }
    },
)
def some_route(param1: str, internal_param: str = "default"):
    """An example route with advanced MCP configuration."""
    return {"param1": param1}
```

In this example, the `/some/route` endpoint is explicitly exposed as a `tool` for the `GET` method only, and the `internal_param` argument is hidden from the tool’s interface.

## Client Examples

Start the server with the appropriate transport and configuration for the client, the default transport is `http`.

```bash
# Start with default settings
openbb-mcp

# Use an alternative transport
openbb-mcp --transport sse

# Start with specific categories and custom host/port
openbb-mcp --default-categories equity,news --host 0.0.0.0 --port 8080

# Start with allowed categories restriction
openbb-mcp --allowed-categories equity,crypto,news

# Disable tool discovery for multi-client usage
openbb-mcp --no-tool-discovery
```

### Claude Desktop:

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

### Cursor:

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

### VS Code

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
