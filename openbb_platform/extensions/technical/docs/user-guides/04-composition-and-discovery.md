# Composition and Discovery

Two utility endpoints round out the extension: `multi` runs many indicators on the same series in one call, and `indicators` introspects the registered router to return a machine-readable catalog.

## multi — many indicators in one call

`multi` dispatches a list of indicator requests against a single input series and merges every numeric output column onto a common date index. Useful for building a feature frame in one round trip.

```python
from openbb import obb

data = obb.equity.price.historical(symbol="SPY", start_date="2023-01-01").results

result = obb.technical.multi(
    data=data,
    indicators=[
        {"indicator": "rsi", "params": {"length": 14}},
        {"indicator": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}},
        {"indicator": "bbands", "params": {"length": 20, "std": 2.0}},
        {"indicator": "atr", "params": {"length": 14}},
    ],
).to_df()

print(result.head())
#               rsi.close_RSI_14  macd.MACD_12_26_9  macd.MACDh_12_26_9  bbands.BBL_20_2.0  ...
# date
# 2023-01-23     46.8              -2.13               0.41                388.74            ...
```

Output column naming is `"<indicator>.<column>"` so you can tell which endpoint produced which value.

Unknown indicator names are silently skipped (so a heterogeneous configuration tolerated). The valid names match the registered router endpoints; see `indicators` (below) for the canonical list.

### When to use multi vs. calling endpoints directly

- **Use `multi`** when you want a feature frame for downstream modelling — you avoid uploading the same OHLCV payload N times and you get one aligned DataFrame.
- **Call endpoints directly** when you care about the per-endpoint output shape (e.g. `bbands` returns three columns plus a bandwidth; the typed `BbandsData` row preserves that structure where `multi` collapses to a flat dict).

## indicators — programmatic catalog

The `indicators` endpoint returns a structured description of every registered router command — name, category, parameters with types and defaults, output columns, and the docstring summary line.

```python
catalog = obb.technical.indicators(category="all").results

print(len(catalog.indicators))      # total endpoints registered
for entry in catalog.indicators:
    summary = entry.description.split("\n", 1)[0]   # first line of the docstring
    print(f"{entry.category:>10s}  {entry.name:<20s}  {summary}")
```

Filter by category to narrow the listing:

```python
overlays = obb.technical.indicators(category="overlay").results
oscillators = obb.technical.indicators(category="oscillator").results
signals = obb.technical.indicators(category="signal").results
```

Categories: `overlay`, `oscillator`, `volatility`, `volume`, `trend`, `signal`, `structure`, `stats`, `multi`, `all`.

### Per-entry shape

Each `IndicatorEntry` carries:

```python
entry = obb.technical.indicators(category="all").results.indicators[0]

entry.name                # str — endpoint name as called via obb.technical.<name>
entry.category            # str — one of the categories above
entry.description         # str — full QueryParams class docstring (first line is the summary)
entry.requires_columns    # list[str] — OHLC(V) columns the endpoint reads from `data`
entry.params              # list[IndicatorParam] — every kwarg besides `data`
entry.output_columns      # list[IndicatorOutputColumn] — every output column
entry.example_call        # dict — a ready-to-invoke kwargs example with default values
```

`IndicatorParam` rows include `name`, `type` (the Python type repr), `default` (or `None` if required), `choices` (the literal values for `Literal[...]` typed fields, otherwise `None`), `description`, and a `constraints` dict carrying `gt`/`ge`/`lt`/`le` bounds where the field declares them.

`IndicatorOutputColumn` rows include `name` (the dict key in the output row), `type`, `nullable`, and `description`.

### Use cases

**Build a UI picker.** Render `entry.params` as form fields with the correct widget per type, with `choices` driving dropdowns and `constraints` (`ge`/`le`/`gt`/`lt`) driving spinners.

**Generate an OpenAPI client.** The catalog mirrors what the OpenAPI schema exposes, but at a higher abstraction level (no FastAPI body-wrapping confusion).

**Drive an LLM tool-call.** Pass the catalog as tool descriptions to a model; it can pick the right indicator and produce the correct `params` dict.

**Validate user input client-side.** Use `parameters[*].choices` and bounds to validate before hitting the server.

## Adding new indicators is automatic

The catalog introspects the registered router at request time, so any endpoint added to `openbb_technical/indicators/`, `openbb_technical/signals/`, or `openbb_technical/multi/` shows up automatically — no separate registry to maintain.

The `__category__` and `__output_columns__` class attributes on each `XxxQueryParams` class drive the category bucket and output-column documentation. Set them on any new endpoint to participate in the catalog.
