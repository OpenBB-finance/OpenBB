# OpenBB JODI Provider

This extension integrates the [Joint Organisations Data Initiative (JODI)](https://www.jodidata.org) data provider into the OpenBB Platform.

JODI publishes free monthly petroleum and natural gas supply, demand, and stock statistics, self-reported by over 100 countries, through the JODI-Oil and JODI-Gas World Databases.

## Installation

To install the extension:

```bash
pip install openbb-jodi
```

## Endpoints

Each endpoint returns one presentation-ready view of the raw data, as a date-indexed table, with the series assessments and units in the results metadata.

### `obb.jodi.oil` — JODI-Oil World Database (monthly, from January 2002)

- `balance` — one country and product; one column per flow of the JODI questionnaire (production, trade, stocks, refinery activity).
- `production` — one primary product; one column per reporting country.
- `demand` — one refined product; one column per reporting country.
- `demand_by_product` — one country; one column per refined product (the demand barrel).
- `imports` / `exports` — one product; one column per reporting country.
- `stocks` — closing stock levels of one product; one column per reporting country.

Units: kb/d, kbbl, kl, kmt, and the barrels/kmt conversion factor.

### `obb.jodi.gas` — JODI-Gas World Database (monthly, from January 2009)

- `balance` — one country; one column per flow of the JODI questionnaire.
- `production` — one column per reporting country.
- `demand` — gross inland deliveries (observed or calculated); one column per reporting country.
- `imports` / `exports` — total, pipeline, or LNG; one column per reporting country.
- `stocks` — closing stock levels; one column per reporting country.

Units: million m3, TJ, and kmt of LNG.

## OpenBB Workspace

The package bundles a "JODI Oil & Gas" app template (`openbb_jodi/assets/apps.json`), served at `/api/v1/jodi/apps.json` and folded into the Workspace app catalogue automatically when running `openbb-api`. It has three dashboards - Country Balances (oil balance, demand barrel, and gas balance, synchronized on one country), Oil Markets, and Gas Markets.

No API key is required. Source tables are cached under the OpenBB user cache directory, partitioned by product and flow; a table is downloaded again only when JODI publishes an update.

Documentation available [here](https://docs.openbb.co/platform/developer_guide/contributing).
