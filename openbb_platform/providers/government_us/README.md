# OpenBB US Government Provider Extensions

This package integrates US Government data sources into the OpenBB Platform, organized as one provider per federal agency. A single install:

```bash
pip install openbb-government-us
```

registers three providers - `congress_gov`, `us_treasury`, and `usda` - plus two API routers, `obb.uscongress` and `obb.ustreasury`. Every endpoint uses public, keyless data; no API keys or registration are required anywhere.

## Congress

Provider: `congress_gov` - Router: `obb.uscongress`

Legislative data for the U.S. Congress, sourced from GovInfo bulk data, the GovInfo link service, the [unitedstates](https://github.com/unitedstates) dataset, and Voteview.

Coverage:

- Bills: lists, metadata, summaries, and full text (`obb.uscongress.bills`, `bill_info`, `bill_text`)
- Enacted laws, public and private (`obb.uscongress.laws`)
- Amendments: lists, details, and text (`obb.uscongress.amendments`, `amendment_info`, `amendment_text`)
- House and Senate calendars (`obb.uscongress.calendars`)
- Congressionally mandated reports (`obb.uscongress.mandated_reports`)
- Committees and committee documents (`obb.uscongress.committee_info`, `committee_documents`)
- Members, their sponsored legislation, and roll-call votes (`obb.uscongress.members`, `member_legislation`, `member_votes`)
- Full-text search across legislative documents (`obb.uscongress.search`)
- Document download URLs for bills, laws, amendments, calendars, reports, and committee documents (the `*_urls` endpoints)

## Treasury

Provider: `us_treasury` - Router: `obb.ustreasury`

Data from the U.S. Department of the Treasury via TreasuryDirect, FedInvest, and the FiscalData API.

TreasuryDirect and FedInvest, served through the standard fixed income router:

- Auction search - announcements and results of marketable securities (`obb.fixedincome.government.treasury_auctions`)
- End-of-day prices for marketable Treasury securities (`obb.fixedincome.government.treasury_prices`)

FiscalData API datasets, served through `obb.ustreasury`:

- Debt to the penny - total public debt outstanding for each business day (`obb.ustreasury.debt_to_penny`)
- Daily Treasury Statement - all 9 tables of cash and debt operations (`obb.ustreasury.daily_statement`)
- Marketable securities scheduled for announcement or auction in the coming week (`obb.ustreasury.upcoming_auctions`)
- Historical auction announcements and results back to 1979 (`obb.ustreasury.auction_results`)
- Treasury Bulletin PDO-1 - regular weekly bill offering results (`obb.ustreasury.weekly_bill_offerings`)

## USDA

Provider: `usda`

Data from the U.S. Department of Agriculture, served through the standard commodity router.

- Foreign Agricultural Service PSD Online - Production, Supply and Distribution reports and time series (`obb.commodity.psd_report`, `obb.commodity.psd_data`)
- Weekly Weather and Crop Bulletin - publication listings and PDF downloads from ESMIS (`obb.commodity.weather_bulletins`, `obb.commodity.weather_bulletins_download`)

## Usage

```python
from openbb import obb

bills = obb.uscongress.bills(congress=118, bill_type="s", provider="congress_gov")
```

```python
debt = obb.ustreasury.debt_to_penny(start_date="2025-01-01", end_date="2025-06-30")
```

```python
auctions = obb.ustreasury.auction_results(security_type="bond", start_date="2020-01-01")
```

```python
corn = obb.commodity.psd_data(commodity="corn", provider="usda")
```

See the OpenBB [documentation](https://docs.openbb.co/python/) and [reference](https://docs.openbb.co/python/reference) for breakdowns of each endpoint.
