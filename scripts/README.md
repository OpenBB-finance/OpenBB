# Developer Scripts

Utility scripts for maintaining OpenBB Platform data and configurations.

## `openbb-update` CLI

The primary way to refresh taxonomy reference data. Ships as a console_script
with `openbb-core`, so it's available after `pip install openbb-core`.

```bash
openbb-update                 # update all taxonomy data
openbb-update exchanges       # update ISO 10383 exchange data only
openbb-update countries       # update country memberships only
openbb-update --dry-run       # preview changes without writing
```

### What it updates

**Exchange data** (`exchange_data.json`):
- Downloads the official ISO 10383 MIC registry from iso20022.org
- Filters to active MICs, extracts name/acronym/city/country/website
- No extra dependencies (stdlib only)

**Country data** (`country_data.json`):
- Reads the existing `country_data.json` as the base (all 249 ISO 3166 countries)
- Strips old group assignments and reapplies from the MEMBERSHIPS dict
- Overlays membership groups: G7, G20, EU, NATO, OECD, OPEC, BRICS
- No extra dependencies (stdlib only, same as exchanges)

### Updating membership lists

When a country joins or leaves a group:
1. Edit the `MEMBERSHIPS` dict in `openbb_core/provider/utils/update_taxonomy.py`
2. Update the `last_updated` date and add notes if relevant
3. Run `openbb-update countries` to regenerate the JSON
4. Commit both the script changes and the updated JSON

### Sources tracked

| Group | Source |
|-------|--------|
| G7 | [Wikipedia](https://en.wikipedia.org/wiki/G7) |
| G20 | [Wikipedia](https://en.wikipedia.org/wiki/G20) |
| EU | [Wikipedia](https://en.wikipedia.org/wiki/Member_state_of_the_European_Union) |
| NATO | [Official NATO website](https://www.nato.int/cps/en/natohq/nato_countries.htm) |
| OECD | [Official OECD website](https://www.oecd.org/about/document/ratification-oecd-convention.htm) |
| OPEC | [Official OPEC website](https://www.opec.org/opec_web/en/about_us/25.htm) |
| BRICS | [Wikipedia](https://en.wikipedia.org/wiki/BRICS) |
| Exchanges | [ISO 20022 MIC Registry](https://www.iso20022.org/market-identifier-codes) |

### CI usage

The same CLI works in CI pipelines. A scheduled workflow can call
`openbb-update --dry-run` to detect drift and open a PR when data changes.
See [#7363](https://github.com/OpenBB-finance/OpenBB/issues/7363) for the
automated refresh proposal.

## Contributing

When adding new scripts:
1. Include comprehensive docstrings with usage examples
2. Document data sources with URLs
3. Add validation/error handling
4. Update this README
