# OpenBB QVERISAI Provider

This extension integrates the [QVERISAI](https://qveris.ai) data provider into the OpenBB Platform.

## Overview

QVERISAI is a third-party API tool platform that provides access to various tools for retrieving and processing data in fields such as finance, economics, healthcare, sports, scientific research, and more.

## Installation

To install the extension:

```bash
pip install openbb-qveris
```

## Configuration

To use QVERISAI, you need to set your API key as an environment variable:

```bash
export QVERIS_API_KEY=your_api_key_here
```

Or in Python:

```python
import os
os.environ["QVERIS_API_KEY"] = "your_api_key_here"
```

You can get an API key from [https://qveris.ai](https://qveris.ai).

## Usage

### Python Interface

```python
from openbb import obb

# Execute a QVERISAI tool
result = obb.qveris.tools.execute(
    tool_id="weather_forecast",
    parameters={"city": "London", "units": "metric"},
    provider="qveris"
)

# Search for tools (note: typically done through MCP server)
tools = obb.qveris.tools.search(
    query="weather forecast",
    provider="qveris"
)
```

### REST API

The provider is also available through the OpenBB REST API:

```bash
POST /api/v1/qveris/tools/execute
{
    "tool_id": "weather_forecast",
    "parameters": {"city": "London", "units": "metric"},
    "provider": "qveris"
}
```

## Features

- **Tool Execution**: Execute any QVERISAI tool with custom parameters
- **Tool Search**: Search for available tools (placeholder for future MCP integration)
- **Error Handling**: Comprehensive error handling and validation
- **Timeout Management**: 5-second timeout as per QVERISAI documentation

## Documentation

For more information, see:
- [QVERISAI Documentation](https://qveris.ai)
- [OpenBB Platform Documentation](https://docs.openbb.co/platform/developer_guide/contributing)

## Notes

According to QVERISAI documentation, tool search is typically done through the MCP server's `search_tools` tool. The REST API primarily supports tool execution. The tool search Fetcher is provided as a placeholder for potential future REST API support or MCP integration.


