# openbb-technical Documentation

The technical extension exposes ~60 endpoints organised into four families:

| Family | What it does | URL prefix |
|---|---|---|
| `indicators/*` | Single-symbol overlays, oscillators, trend, volume, volatility, structure, statistics | `/` (root) |
| `signals/*` | Event detectors: crossovers, divergences, breakouts, candlestick patterns, regime | `/signals/` |
| `multi/*` | Multi-symbol correlation, screening, relative-rotation, multi-indicator composition, catalog | `/` (root, except `correlation_matrix` and `screen` which expose `multi.*`) |
| `relative_rotation` | JdK RS-Ratio + RS-Momentum for a benchmark-anchored basket | `/` (root) |

Every endpoint is reachable through three transports:

1. **Python**: `from openbb import obb; obb.technical.<endpoint>(...)`
2. **HTTP**: `POST http://localhost:8000/api/v1/technical/<endpoint>` (run `openbb-api` to start the server)
3. **CLI**: `openbb -i` then `/technical/<endpoint>`

## Where to start

- **First time?** [getting-started.md](./getting-started.md) shows installation, the three transports, and a 5-line example for each.
- **Building a strategy?** [user-guides/01-indicators.md](./user-guides/01-indicators.md) covers single-symbol indicator workflows.
- **Want trade signals?** [user-guides/02-signals.md](./user-guides/02-signals.md) covers the signals subrouter.
- **Working with a basket?** [user-guides/03-multi-symbol.md](./user-guides/03-multi-symbol.md) covers correlation, screening, and Relative Rotation Graphs.
- **Composing pipelines?** [user-guides/04-composition-and-discovery.md](./user-guides/04-composition-and-discovery.md) covers the `multi` and `indicators` (catalog) endpoints.
- **Looking up a specific endpoint?** [api-reference.md](./api-reference.md) lists every endpoint with its parameters, output columns, and a one-line description.

## Conventions

- **Input**: every data-consuming endpoint accepts the same shapes — `list[Data]`, `list[dict]`, `pandas.DataFrame`, `pandas.Series`, or `numpy.ndarray`. The library converts between them automatically.
- **Output**: every endpoint returns an `OBBject`. The numeric payload is on `.results` as a list of typed Pydantic models.
- **Validation**: every endpoint validates its inputs through a `XxxQueryParams` Pydantic class and emits its rows through a `XxxData` (or `XxxEvent`/`XxxSignal`) class. The class docstrings carry full NumPy-format `Parameters` and `Returns` sections.
- **Discovery**: the `indicators` endpoint introspects the registered router and returns a structured catalog — useful for building UI pickers, OpenAPI clients, or LLM tool-calls without hard-coding endpoint names.
