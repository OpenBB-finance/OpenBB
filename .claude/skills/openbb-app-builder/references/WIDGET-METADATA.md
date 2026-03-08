# Widget Metadata Reference

Complete guide for defining widget metadata specifications.

## Widget Types Reference

Choose the appropriate widget type for each data view:

| Type | Use Case | Example | Grouping Support | HTTP Method |
|------|----------|---------|------------------|-------------|
| `table` | Tabular data with rows/columns | Holdings, Transactions, Stock lists | Yes | GET |
| `table_ssrm` | Large datasets (200k+ rows) with server-side pagination/filtering/sorting | Big databases, Logs | Yes | GET |
| `chart` | Plotly visualizations | Price charts, Performance graphs | Yes | GET |
| `chart-highcharts` | Highcharts visualizations | Alternative charting library | Yes | GET |
| `metric` | KPI values with deltas | Portfolio value, Daily P&L | Yes | GET |
| `markdown` | Formatted text content | Summaries, Reports, Analysis | Yes | GET |
| `newsfeed` | Article lists | News, Research reports | Yes | GET |
| `html` | Custom HTML (no JS executed) | Styled dashboards, Custom viz | Yes | GET |
| `multi_file_viewer` | PDF/CSV/TXT file viewer | Documents, Reports, Spreadsheets | Yes | GET |
| `advanced-chart` | TradingView professional charts | Professional charting with indicators | **NO** | GET |
| `live_grid` | Real-time table with WebSocket updates | Live prices, Order book | Yes | GET + WS |
| `omni` | Dynamic multi-format content | AI responses, Mixed content | Yes | **POST** |
| `note` | Editable note widget | Research notes, Prompts | N/A | N/A |
| `youtube` | YouTube video embed | Tutorials, Market commentary | N/A | N/A |

**Warning**: `advanced-chart` (TradingView) does NOT support parameter-based grouping. Use `chart` (Plotly) if you need a chart that updates when clicking a watchlist row.

---

## Widget-Level Properties

All properties available on each widget entry in `widgets.json`:

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `name` | string | Yes | — | Display name shown to users |
| `description` | string | Yes | — | Brief description (shown in UI and used by Copilot AI) |
| `endpoint` | string | Yes | — | Backend API endpoint path |
| `type` | string | No | `"table"` | Widget type (see table above) |
| `category` | string | No | — | Widget organization category |
| `subCategory` | string | No | — | Secondary categorization |
| `source` | array | No | — | Data source identifiers |
| `imgUrl` | string | No | — | Preview image URL |
| `raw` | boolean | No | `false` | Enable chart/raw data toggle button |
| `runButton` | boolean | No | `false` | Show run button instead of auto-refresh |
| `refetchInterval` | number/false | No | `900000` | Auto-refresh interval in ms (min: 1000, `false` to disable) |
| `staleTime` | number | No | `300000` | Time in ms until cached data is considered stale |
| `wsEndpoint` | string | No | — | WebSocket endpoint for live updates (used with `live_grid`) |
| `ai` | boolean | No | `true` | When `false`, hides widget from AI/Copilot access |

---

## Grid Layout (gridData)

| Property | Type | Max | Description |
|----------|------|-----|-------------|
| `w` | number | 40 | Width in grid columns |
| `h` | number | 100 | Height in grid rows |
| `minW` | number | — | Minimum width constraint |
| `minH` | number | — | Minimum height constraint |
| `maxW` | number | 40 | Maximum width constraint |
| `maxH` | number | 100 | Maximum height constraint |

**Grid system**: 40-column layout. Minimum recommended width: 10 columns.

---

## Parameter Types Guide

### Common Parameter Properties

All parameter types share these properties:

| Property | Type | Description |
|----------|------|-------------|
| `paramName` | string | URL query parameter name (required) |
| `type` | string | Parameter type (required) |
| `label` | string | Display label in UI |
| `description` | string | Tooltip text on hover |
| `value` | any | Default value; use `null` for unset |
| `show` | boolean | Whether to display in UI (default: `true`) |
| `multiple` | boolean | Allow ad-hoc user-entered options in dropdown |
| `multiSelect` | boolean | Allow selecting multiple values |
| `style` | object | Styling options, e.g. `{"popupWidth": 400}` (200-1000) |

### Text Input
```json
{
  "paramName": "query",
  "type": "text",
  "label": "Search Query",
  "description": "Enter search term",
  "value": ""
}
```

### Ticker Input
```json
{
  "paramName": "symbol",
  "type": "ticker",
  "label": "Symbol",
  "value": "AAPL"
}
```
Provides a dedicated ticker/symbol input with autocomplete.

### Number Input
```json
{
  "paramName": "limit",
  "type": "number",
  "label": "Limit",
  "value": 10
}
```

### Boolean Toggle
```json
{
  "paramName": "include_extended",
  "type": "boolean",
  "label": "Include Extended Hours",
  "value": false
}
```

### Date Picker
```json
{
  "paramName": "start_date",
  "type": "date",
  "label": "Start Date",
  "value": "$currentDate-1M"
}
```
Date modifiers: `$currentDate`, `$currentDate±[n]h` (hours), `$currentDate±[n]d` (days), `$currentDate±[n]w` (weeks), `$currentDate±[n]M` (months), `$currentDate±[n]y` (years). Supports both `+` and `-` directions.

### Static Dropdown
```json
{
  "paramName": "interval",
  "type": "text",
  "label": "Interval",
  "value": "1d",
  "options": [
    {"label": "1 Day", "value": "1d"},
    {"label": "1 Week", "value": "1w", "extraInfo": "Weekly aggregation"},
    {"label": "1 Month", "value": "1m"}
  ]
}
```
Options support an optional `extraInfo` field for additional context.

### Dynamic Dropdown (from endpoint)
```json
{
  "paramName": "symbol",
  "type": "endpoint",
  "label": "Select Symbol",
  "optionsEndpoint": "/symbols",
  "multiSelect": false
}
```

### Dependent Dropdown
```json
{
  "paramName": "city",
  "type": "endpoint",
  "label": "City",
  "optionsEndpoint": "/cities",
  "optionsParams": {"country": "$country"}
}
```
The `$country` reference causes this dropdown to re-fetch options whenever the `country` parameter changes.

### Form Parameter
```json
{
  "paramName": "config",
  "type": "form",
  "label": "Configuration"
}
```
Renders a form-style input group.

### Tabs Parameter
```json
{
  "paramName": "view",
  "type": "tabs",
  "label": "View",
  "options": [
    {"label": "Overview", "value": "overview"},
    {"label": "Details", "value": "details"}
  ]
}
```
Renders as tab-style selector in the widget header.

### File Selector (for multi_file_viewer)
```json
{
  "paramName": "file",
  "type": "endpoint",
  "label": "Select File",
  "optionsEndpoint": "/files",
  "roles": ["fileSelector"],
  "multiSelect": true
}
```

---

## Column Definition Guide

### All Column Properties

| Property | Type | Description |
|----------|------|-------------|
| `field` | string | JSON field name from data (required) |
| `headerName` | string | Display column header |
| `cellDataType` | string | Data type for the cell |
| `chartDataType` | string | How column is used in chart view |
| `formatterFn` | string | Value formatting function |
| `renderFn` | string/array | Cell rendering function(s) |
| `renderFnParams` | object | Parameters for renderFn |
| `align` | string | Text alignment: `"left"`, `"center"`, `"right"` |
| `width` | number | Fixed column width in pixels |
| `minWidth` | number | Minimum column width in pixels |
| `maxWidth` | number | Maximum column width in pixels |
| `hide` | boolean | Hide column by default |
| `pinned` | string | Pin column: `"left"` or `"right"` |
| `headerTooltip` | string | Tooltip shown on column header hover |
| `prefix` | string | Text prepended before cell value |
| `suffix` | string | Text appended after cell value |
| `enableCellChangeWs` | boolean | Enable WebSocket cell updates (default: `true`) |

### Cell Data Types
- `text` - String values
- `number` - Numeric values
- `boolean` - True/false
- `date` - Date objects
- `dateString` - Date as string
- `object` - Complex objects

### Chart Data Types

Controls how a column behaves when the table is viewed as a chart:
- `category` - Used as category/x-axis labels
- `series` - Used as data series/y-axis values
- `time` - Used as time axis
- `excluded` - Excluded from chart view

### Formatter Functions

**CRITICAL**: Only these values are valid for `formatterFn`:
- `int` - Integer formatting (rounds to whole number)
- `none` - No formatting (use for currency/decimal display)
- `percent` - Percentage formatting
- `normalized` - Normalize to scale
- `normalizedPercent` - Normalized percentage
- `dateToYear` - Extract year from date

**Common Error**: `"currency"` is NOT a valid formatterFn value. Use `"none"` for currency values instead.

### Render Functions
- `greenRed` - Positive values green, Negative values red
- `titleCase` - Capitalize words
- `hoverCard` - Show markdown content on hover
- `cellOnClick` - Action triggered on cell click (watchlist pattern)
- `columnColor` - Conditional cell coloring based on rules
- `showCellChange` - Animate value changes (useful for live_grid)

Multiple render functions can be applied as an array: `"renderFn": ["greenRed", "titleCase"]`

### renderFnParams: cellOnClick with groupBy (Watchlist Pattern)

Make table cells clickable to update other widgets in the same group:

```json
{
    "field": "symbol",
    "headerName": "Symbol",
    "cellDataType": "text",
    "pinned": "left",
    "renderFn": "cellOnClick",
    "renderFnParams": {
        "actionType": "groupBy",
        "groupByParamName": "symbol",
        "valueField": "ticker"
    }
}
```

- `actionType`: `"groupBy"` — updates grouped widgets
- `groupByParamName`: The parameter name to update in grouped widgets
- `valueField` (optional): Use a different field's value instead of the clicked cell's value

**Requirements for this pattern:**
1. Both table and target widget must be in the same group (`"groups": ["Group 1"]`)
2. Target widget MUST support param grouping (NOT `advanced-chart`)
3. Both widgets need matching `paramName` with `type: "endpoint"`
4. Group names MUST follow "Group N" pattern

### renderFnParams: cellOnClick with sendToAgent

Send cell data to an AI agent:

```json
{
    "field": "summary",
    "renderFn": "cellOnClick",
    "renderFnParams": {
        "actionType": "sendToAgent",
        "markdown": "Analyze this: {symbol} - {summary}",
        "agentId": "my-agent"
    }
}
```

- `markdown`: Template string with `{field}` variable interpolation
- `agentId` (optional): Target a specific agent

### renderFnParams: columnColor

Conditional cell coloring based on value rules:

```json
{
    "field": "score",
    "renderFn": "columnColor",
    "renderFnParams": {
        "colorRules": [
            {"condition": "gte", "value": 80, "color": "#22c55e", "fill": true},
            {"condition": "between", "range": {"min": 50, "max": 79}, "color": "#f59e0b"},
            {"condition": "lt", "value": 50, "color": "#ef4444", "fill": true}
        ]
    }
}
```

Available conditions: `eq`, `ne`, `gt`, `lt`, `gte`, `lte`, `between`, `contains`, `notContains`
- `value`: Comparison value (number or string)
- `range`: `{min, max}` — required for `between` condition
- `color`: Hex or named color
- `fill`: Boolean — fill cell background (default: text color only)

### renderFnParams: hoverCard

Show rich content on hover:

```json
{
    "field": "name",
    "renderFn": "hoverCard",
    "renderFnParams": {
        "cellField": "name",
        "title": "Details for {name}",
        "markdown": "**Sector**: {sector}\n**Industry**: {industry}\n\n{description}"
    }
}
```

### Sparkline Columns

Add inline charts within table cells:

```json
{
    "field": "price_history",
    "headerName": "Trend",
    "cellDataType": "object",
    "renderFn": "sparkline",
    "renderFnParams": {
        "type": "line",
        "dataField": "prices",
        "options": {
            "stroke": "#3b82f6",
            "strokeWidth": 2,
            "fill": "rgba(59,130,246,0.1)",
            "fillOpacity": 0.3,
            "min": 0,
            "direction": "horizontal",
            "markers": {
                "enabled": true,
                "size": 3,
                "fill": "#3b82f6",
                "stroke": "#ffffff",
                "strokeWidth": 1
            },
            "pointsOfInterest": {
                "firstLast": true,
                "minimum": true,
                "maximum": true
            },
            "padding": {"top": 2, "right": 2, "bottom": 2, "left": 2}
        }
    }
}
```

Sparkline types: `"line"`, `"area"`, `"bar"`
- `dataField`: Alternative field name if data is nested
- `direction`: `"horizontal"` or `"vertical"`

---

## Table Configuration (data.table)

Additional properties on the `data.table` object:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enableCharts` | boolean | — | Enable built-in AgGrid chart visualization toggle |
| `showAll` | boolean | — | Display all data without pagination |
| `transpose` | boolean | — | Transpose rows and columns |
| `enableAdvanced` | boolean | — | Show "Columns" side tab for column management |
| `enableFormulas` | boolean | — | Show "Formulas" side tab for Excel-like formulas |
| `columnsDefs` | array | — | Column definition objects (see above) |

### chartView (Table-to-Chart Default View)

Configure the default chart view when table data is visualized as a chart:

```json
{
    "data": {
        "table": {
            "columnsDefs": [],
            "chartView": {
                "enabled": true,
                "chartType": "groupedColumn",
                "cellRangeCols": {
                    "groupedColumn": ["category", "series1", "series2"]
                },
                "ignoreCellRange": false
            }
        }
    }
}
```

**Available chartType values:**
- Column: `column`, `groupedColumn`, `stackedColumn`, `normalizedColumn`
- Bar: `bar`, `groupedBar`, `stackedBar`, `normalizedBar`
- Line: `line`
- Area: `area`, `stackedArea`, `normalizedArea`
- Scatter/Bubble: `scatter`, `bubble`
- Pie: `pie`, `donut` (alias: `doughnut`)
- Radar: `radarLine`, `radarArea`
- Specialized: `histogram`, `nightingale`, `radialColumn`, `radialBar`, `sunburst`, `rangeBar`, `rangeArea`, `boxPlot`, `treemap`, `heatmap`, `waterfall`

---

## SSRM (Server-Side Row Model) Configuration

For large datasets (200k+ rows). Uses `type: "table_ssrm"`.

The backend endpoint receives query parameters for server-side operations:
- `startRow` / `endRow` — pagination range
- Sort model and filter model passed as query params

Supports server-side: pagination, filtering (text/number/set), sorting (multi-column), and row grouping with aggregation.

**AI limitation**: AI agents can only analyze currently visible/loaded rows, not the full dataset.

---

## Omni Widget Configuration

The omni widget uses **POST** requests and can return different content formats dynamically.

```json
{
    "omni_widget": {
        "name": "AI Analysis",
        "type": "omni",
        "endpoint": "/omni-analysis",
        "params": [
            {
                "paramName": "prompt",
                "type": "text",
                "label": "Prompt",
                "value": "",
                "language": "sql"
            }
        ]
    }
}
```

**Backend receives POST body** (not query params):
```python
@app.post("/omni-analysis")
async def omni_endpoint(data: str | dict = Body(...)):
    prompt = data.get("prompt") if isinstance(data, dict) else data
```

**Response format** with `data_format.parse_as`:
```python
# Text/Markdown response
return {"content": "# Analysis\nResults...", "data_format": {"data_type": "markdown", "parse_as": "text"}}

# Table response
return {"content": [{"col1": "val1"}], "data_format": {"data_type": "json", "parse_as": "table"}}

# Chart response (Plotly)
return {"content": plotly_fig_dict, "data_format": {"data_type": "json", "parse_as": "chart"}}
```

Parameter `language` enables syntax highlighting: `"sql"`, `"python"`, or omit for plain text.

---

## File Viewer Configuration

Use `type: "multi_file_viewer"` for document viewing.

**Two delivery methods:**

1. **Base64 encoding** (smaller files):
```python
return {
    "content": base64_encoded_string,
    "data_format": {"data_type": "pdf", "filename": "report.pdf"}
}
```

2. **URL reference** (larger files, cloud storage):
```python
return {
    "content": None,
    "file_reference": "https://presigned-url.example.com/report.pdf",
    "data_format": {"data_type": "pdf", "filename": "report.pdf"}
}
```

Supported `data_type` values: `"pdf"`, `"csv"`, `"txt"`, and other file formats.

Use `roles: ["fileSelector"]` on the parameter for file selection UI.

---

## HTML Widget Notes

- Renders server-generated HTML content
- **JavaScript will NOT execute** (security restriction)
- Use CSS animations instead of JS for dynamic effects
- Use CSS flexbox/grid for responsive layouts
- All data processing must happen server-side
- Return `HTMLResponse` from FastAPI endpoint

---

## Live Grid (WebSocket) Configuration

For real-time updating tables:

```json
{
    "live_prices": {
        "name": "Live Prices",
        "type": "live_grid",
        "endpoint": "/prices",
        "wsEndpoint": "/ws/prices",
        "data": {
            "table": {
                "columnsDefs": [
                    {"field": "price", "renderFn": "showCellChange", "enableCellChangeWs": true}
                ]
            }
        }
    }
}
```

- `wsEndpoint`: WebSocket endpoint for streaming updates
- `enableCellChangeWs`: Enable cell-level WebSocket updates (default: `true`)
- `showCellChange` renderFn: Animates value changes visually

---

## MCP Tool Matching

For AI/Copilot integration, widgets can map to MCP tools:

```json
{
    "mcp_server": "my-server",
    "tool_id": "get-stock-data"
}
```

Both fields use exact string matching.

---

## Widget Definition Template

For each widget, define:

```markdown
### Widget: {widget_id}

#### Basic Info
- **Name**: {Display name}
- **Description**: {Brief description}
- **Type**: {widget type}
- **Category**: {Category name}

#### Layout
- **Default Width (w)**: {10-40}
- **Default Height (h)**: {4-20}

#### Endpoint
- **HTTP Method**: {GET | POST}
- **Path**: /{widget_id}
- **Parameters**: {see params section}

#### Parameters
| Name | Type | Label | Default | Required |
|------|------|-------|---------|----------|
| symbol | endpoint | Symbol | AAPL | Yes |
| period | text | Period | 1M | No |

#### Data Format

**Response Type**: {JSON Array | JSON Object | Plotly JSON}

**Example Response**:
```json
{example response}
```

#### For Table Widgets: Column Definitions

| Field | Header | Type | Format | Render |
|-------|--------|------|--------|--------|
| symbol | Symbol | text | - | pinned: left |
| price | Price | number | int | - |
| change | Change % | number | percent | greenRed |
```

---

## Best Practices

### runButton Configuration
- **Default to `runButton: false`** (or omit entirely)
- Only set `runButton: true` for:
  - Heavy computations (Monte Carlo simulations, complex ML models)
  - Expensive API calls with rate limits
  - Operations that take >5 seconds

### Widget Height Guidelines
| Widget Type | Recommended Height |
|-------------|-------------------|
| metric | 4-6 |
| table (small) | 8-12 |
| table (medium) | 12-15 |
| chart | 12-15 |
| newsfeed | 12-15 |
| markdown | 8-12 |
| html | 10-15 |
| omni | 12-18 |

Avoid heights above 20 unless specifically needed.

### Chart Widget Best Practices

**Prefer AgGrid Charts over Plotly when possible:**
- AgGrid allows users to access underlying raw data
- Users can create their own visualizations from the data

**When using Plotly charts:**
1. **Do NOT include title** - The widget already has a name/title
2. **Always support `raw` parameter** - Return raw data array when `raw=True`
3. **Support `theme` parameter** - Adapt colors for dark/light mode

### Refresh & Caching
- `refetchInterval`: Controls auto-refresh (default: 15 min / 900000ms, minimum: 1s / 1000ms)
- `staleTime`: How long cached data is considered fresh (default: 5 min / 300000ms)
- Set `refetchInterval: false` to disable auto-refresh entirely
- For live data, use `live_grid` with WebSocket instead of aggressive polling

### AI Visibility
- Widgets are visible to AI/Copilot by default (`ai: true`)
- Set `ai: false` to hide sensitive or experimental widgets from AI access
- AI can read widget metadata, parameters, and data to answer user questions

### widgets.json Format
- **Must be object format**: `{"widget_id": {...}}`
- **NOT array format**: `[{...}]` will be rejected
- Widget IDs become the keys
