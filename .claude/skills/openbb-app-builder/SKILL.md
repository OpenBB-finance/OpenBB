---
name: openbb-app-builder
description: Build custom backends and widgets for OpenBB Workspace. Use when user wants to create an OpenBB app, convert Streamlit/Gradio apps, or build dashboards. Handles the full pipeline from requirements to deployment.
---

# OpenBB App Builder

You are an expert OpenBB app developer. This skill handles the complete pipeline for building OpenBB Workspace apps - from requirements gathering to tested deployment.

## Quick Reference

| Command | Action |
|---------|--------|
| "Build an OpenBB app for X" | Full pipeline |
| "Convert this Streamlit app" | Reference-based build |
| "Quick mode: build X" | Minimal questions |

## Execution Modes

| Mode | Triggers | Behavior |
|------|----------|----------|
| **Standard** | (default) | Confirm at each phase, detailed explanations |
| **Quick** | "quick mode", "fast", "minimal" | Sensible defaults, single final confirmation |
| **Reference** | Code snippets, "convert this", "like this app" | Auto-analyze code, extract components, map to OpenBB |
| **Verbose** | "verbose", "teach me", "explain" | Educational approach, explain decisions |

**Mode detection**: Check user's first message for trigger phrases. Default to Standard if unclear.

## Pipeline Overview

```
Phase 1: Interview      → Gather requirements, analyze references
Phase 2: Widgets        → Define widget metadata
Phase 3: Layout         → Design dashboard layout
Phase 4: Plan           → Generate implementation plan
Phase 5: Build          → Create all files
Phase 6: Validate       → Run validation scripts
Phase 6.5: Browser Val  → Test against OpenBB Workspace (recommended)
Phase 7: Test           → Browser testing (optional)
```

For full architecture details, error recovery patterns, and troubleshooting, see [ARCHITECTURE.md](references/ARCHITECTURE.md).

## Phase Execution

### Phase 1: Requirements Interview

**Goal**: Gather complete requirements before writing code.

**Two modes**:
1. **Interactive** - Ask structured questions about data, widgets, auth
2. **Reference** - Analyze Streamlit/Gradio/React code and extract components

For detailed interview process and component mapping, see [APP-INTERVIEW.md](references/APP-INTERVIEW.md).

**Output**: Create `{app-name}/APP-SPEC.md` with requirements.

---

### Phase 2: Widget Metadata

**Goal**: Define every widget with complete specifications.

For each widget, define:
- Type (table, chart, metric, etc.)
- Parameters and their types
- Column definitions (for tables)
- Data format

For complete widget type reference and parameter guide, see [WIDGET-METADATA.md](references/WIDGET-METADATA.md).

**Output**: Append widget definitions to APP-SPEC.md.

---

### Phase 3: Dashboard Layout

**Goal**: Design visual layout with tabs and positioning.

- OpenBB uses a 40-column grid
- Organize widgets into logical tabs
- Define parameter groups for synced widgets

**CRITICAL**: Group names must follow "Group 1", "Group 2" pattern - custom names fail silently.

For layout templates and ASCII design guide, see [DASHBOARD-LAYOUT.md](references/DASHBOARD-LAYOUT.md).

**Output**: Append layout to APP-SPEC.md.

---

### Phase 4: Implementation Plan

**Goal**: Generate step-by-step build plan.

For plan structure and templates, see [APP-PLANNER.md](references/APP-PLANNER.md).

**Output**: Create `{app-name}/PLAN.md`.

---

### Phase 5: Build

**Goal**: Create all application files.

Files to create:
- `main.py` - FastAPI app with endpoints
- `widgets.json` - Widget configurations
- `apps.json` - Dashboard layout
- `requirements.txt` - Dependencies
- `.env.example` - Environment template

For core implementation patterns and widget type details, see [OPENBB-APP.md](references/OPENBB-APP.md).

---

### Phase 6: Validation

**Goal**: Validate all generated files.

For validation commands and error handling, see [VALIDATE.md](references/VALIDATE.md).

If errors, fix and re-validate (max 3 retries).

---

### Phase 6.5: Browser Validation (Highly Recommended)

**Goal**: Validate against OpenBB Workspace's actual schema.

Static validation cannot catch all issues. Browser validation against `pro.openbb.co` is the most reliable method.

See [VALIDATE.md](references/VALIDATE.md#browser-validation-highly-recommended) for steps and common errors.

---

### Phase 7: Browser Testing (Optional)

**Goal**: Test in real browser with OpenBB Workspace.

For browser testing procedures, see [APP-TESTER.md](references/APP-TESTER.md).

---

## Core Implementation Reference

### Backend Structure

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pro.openbb.co",
        "https://pro.openbb.dev",
        "http://localhost:1420"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load apps.json at startup
APPS_FILE = Path(__file__).parent / "apps.json"
with open(APPS_FILE) as f:
    APPS_CONFIG = json.load(f)

@app.get("/widgets.json")
def get_widgets():
    return {  # MUST be dict, NOT array
        "widget_id": {
            "name": "Widget Name",
            "type": "table",
            "endpoint": "my_endpoint"
        }
    }

@app.get("/apps.json")
def get_apps():
    return APPS_CONFIG  # MUST be object, NOT array
```

### Widget Types

| Type | Use Case |
|------|----------|
| `table` | Tabular data with sorting/filtering |
| `chart` | Plotly visualizations |
| `metric` | KPI values with labels |
| `markdown` | Formatted text |
| `newsfeed` | Article lists |

### Best Practices

1. **No `runButton: true`** unless heavy computation (>5 seconds)
2. **Reasonable heights**: metrics h=4-6, tables h=12-18, charts h=12-15
3. **widgets.json must be dict** format with widget IDs as keys
4. **apps.json must be object** format (NOT array), served via `/apps.json` endpoint
5. **Plotly charts**: No title (widget provides it), support `raw` param
6. **Group names**: Must be "Group 1", "Group 2" etc. with `name` field in group object

For complete apps.json structure and required fields, see [OPENBB-APP.md](references/OPENBB-APP.md#appsjson-structure).

For pre-deployment checklist and browser validation, see [VALIDATE.md](references/VALIDATE.md#pre-deployment-checklist).

---

## Directory Structure Created

```
{app-name}/
├── APP-SPEC.md        # Requirements
├── PLAN.md            # Implementation plan
├── main.py            # FastAPI application
├── widgets.json       # Widget configs
├── apps.json          # Dashboard layout
├── requirements.txt   # Dependencies
└── .env.example       # Environment template
```

---

## Completion

On success:
```
App created at {app-name}/

To run:
  cd {app-name}
  pip install -r requirements.txt
  uvicorn main:app --reload --port 7779

To add to OpenBB:
  Settings → Data Connectors → Add: http://localhost:7779
```
