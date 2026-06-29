# openbb-government-ca

Canadian government data provider extension for the OpenBB Platform.

This extension bundles two Canadian public-sector data sources into a
single, self-contained OpenBB V5 provider:

| Source | Coverage | Access pattern |
|---|---|---|
| **Bank of Canada** (BoC) | FX rates, policy rate, benchmark bond yields | Valet JSON API |
| **Statistics Canada** (StatsCan) | Economic indicators, key monthly series | SDMX 2 REST + ind-econ JSON |

## OpenBB V5 packaging

This extension follows the **Hatchling build-hook pattern** introduced
by `openbb-oecd` (PR #7413). At install time, a build hook
(`hatch_build.py`) invokes `openbb_government_ca/utils/generate_cache.py`
to fetch a metadata snapshot from upstream APIs and bundle it as a
compressed JSON asset (`assets/government_ca_cache.json.xz`) inside the
wheel and sdist. At runtime, the metadata is read from that shipped
asset — **no network calls are made to resolve dataset identifiers,
codelists, or series labels**. Network calls happen only when the user
actually requests observations.

The cache file is gitignored; it is regenerated on every build. Set
`OPENBB_GOVERNMENT_CA_FORCE_CACHE_REBUILD=1` to force a rebuild even if
the file already exists locally.

## Installation

```bash
# From the OpenBB monorepo:
uv pip install -e ./openbb_platform/providers/government_ca

# Standalone:
uv pip install openbb-government-ca
```

## Usage

```python
from openbb import obb

# Bank of Canada — FX
df = obb.boc.fx(symbol="USDCAD", start_date="2024-01-01").to_df()

# Bank of Canada — policy overnight rate
df = obb.boc.rates(start_date="2024-01-01").to_df()

# Bank of Canada — benchmark bond yield curve
df = obb.boc.yields(start_date="2024-01-01").to_df()

# Statistics Canada — key economic indicators
df = obb.statscan.economic_indicators(start_date="2024-01-01").to_df()
```

## Development

```bash
# Regenerate the cache locally (skips the build hook)
generate-government-ca-cache

# Lint + format
ruff --format openbb_government_ca tests
ruff --check openbb_government_ca tests

# Type-check
ty --check

# Run tests (cassettes are pre-recorded — no network needed)
pytest
```

## License

AGPL-3.0-only
