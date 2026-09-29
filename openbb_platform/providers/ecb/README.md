# OpenBB ECB Provider

This extension integrates the [European Central Bank (ECB) Data Portal](https://data.ecb.europa.eu/)
into the OpenBB Platform. It is a self-registering extension: when the `economy`, `currency`, and
`fixedincome` extensions are absent, every model is exposed under its own `obb.ecb.*` router; when
they are installed, the ECB fetchers plug into their canonical commands (e.g.
`obb.economy.balance_of_payments(provider="ecb")`).

## Installation

```bash
pip install openbb-ecb
```

## Coverage

**Full SDMX 2.1 catalogue sweep**

- `available_indicators` — the **series builder**: enumerate the **individual series
  (indicators)** within a dataflow (SDMX `serieskeysonly`), narrowed by `frequency` and
  `reference_area` dependent dropdowns (their options adapt to the selected dataflow), a
  `dimension_values` text field for the dataflow's other dimensions (`DIM:VALUE`), and a text
  `query`; each row is a ready `FLOW::KEY` symbol (e.g. the ~60k HICP series under `ICP`). In the
  Workspace you **click a row's symbol** (`cellOnClick`) to load it in the `indicators` widget. A
  *dataflow* is the table; a *series* is the indicator (with its transformation — index, rate, …).
- `indicators` — fetch any ECB series by a `FLOW::KEY` symbol, e.g. `EXR::D.USD.EUR.SP00.A`.
- `list_dataflows`, `search_dataflows`, `list_topics`, `topic_dataflows`,
  `get_dataflow_dimensions`, `dimension_choices` — dataflow discovery & progressive key building.

**Concepts & dataset metadata**

- `list_concepts` — the ECB data-portal **concepts** (the portal's curated topics, e.g. *Bank
  interest rates*, *Monetary aggregates*, *HICP*), each grouping the datasets it covers.
- `dataflow_information` — an **HTML** widget serving a dataset's full ECB reference metadata —
  Scope, Methodological information, Statistical processing, Administrative information, Quality,
  Dissemination, Legal and institutional environment, Technical information (with the downloadable
  series catalogue) and Miscellaneous. Pick a concept, then a dataset. This rich metadata for
  every dataflow is materialised into the shipped cache at build time.

**Presentation tables**

- `list_tables` — the ECB data-portal presentation ("release") tables (e.g. the monetary
  aggregates or the HICP), the full curated set enumerated from the portal's publications
  tree and grouped by its categories.
- `presentation_table` — every series a table publishes as a wide row: its concise `title`,
  the full series definition on hover, its `unit`, and the most recent periods pivoted into
  columns as **real, unit-scaled numbers** (each value expanded by the series' `UNIT_MULT`
  from the SDMX schema). Labels, values and units are resolved at request time from each
  series' `TITLE` / `TITLE_COMPL` / `UNIT` / `UNIT_MULT`; the cache stores only each table's
  title, portal placement and full series list.

**Standardized timeseries**

- `exchange_rates` — euro reference exchange rates (EXR), EUR pairs and derived cross rates.
- `reference_rates` — the latest euro foreign-exchange reference rates.
- `key_interest_rates` — the key ECB rates (deposit, lending, refinancing) from FM.
- `euro_short_term_rate` — the €STR and its full detail (EST).
- `mfi_interest_rates` — MFI/bank interest rates on euro-area loans & deposits (MIR).
- `yield_curve` — euro area government bond yield curves.
- `balance_of_payments` — euro area balance of payments.

**Releases, documents & calendar**

- `release_choices` / `release_document` — ECB press releases, publications, and blog posts (RSS).
  `release_choices` lists a feed's posts (newest first) and feeds the **HTML** widget's `release`
  dropdown; `release_document` is the ECB Release Viewer (`type: "html"`), which serves the chosen
  article as a full page — its own CSS, charts, tables and images intact, URLs resolved to absolute
  with an injected `<base>` so it renders exactly as ECB published it.
- `calendar` — the ECB statistical release calendar. In the Workspace it is the app's **entry
  point**: each row's `Dataset` cell (`cellOnClick`) sets the shared `dataflow`, so picking a
  release drives the dataflow-dimensions and series-builder widgets to explore that release's data.
- `eligible_assets` — the Eurosystem list of eligible marketable (collateral) assets.

## Caching

Two independent caches:

- A shipped, read-only **SDMX metadata cache** (`assets/ecb_cache.json.xz`), materialized at build
  time by `generate-ecb-cache`.
- A **parsed-data disk cache** (`diskcache`) for fetched results, with per-dataset TTLs matched to
  ECB release cadence. The directory is `OPENBB_ECB_CACHE_DIR`, or
  `<cache_directory>/ecb/data` from the OpenBB layered config. Set `OPENBB_ECB_NO_CACHE=1` to
  disable it; most data commands also accept `use_cache=False`.

Documentation available [here](https://docs.openbb.co/odp/python).
