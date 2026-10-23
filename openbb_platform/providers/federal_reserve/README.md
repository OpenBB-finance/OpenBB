# OpenBB Federal Reserve Provider

This extension integrates [Federal Reserve](https://www.federalreserve.gov/data.htm) data into the OpenBB Platform: Federal Reserve Board statistics not published to FRED, research and survey data from the twelve regional Reserve Banks, and FFIEC bank-supervision and regulatory reports. No authorization is required for access.

The FFIEC integration supplies high-quality output that is ready-to-use and fully parsed. Data is suitable for finance professionals, banking industry analysts, data scientists, AI analysis, and proprietary research.

## Installation

To install the extension:

```bash
pip install openbb-federal-reserve
```

Then build the Python static assets by running:

```sh
openbb-build
```

## Quick Start

The fastest way to get started is by connecting to the OpenBB Workspace as a custom backend.

Install the launcher package:

```bash
pip install openbb-platform-api
```

### Start Server

```sh
openbb-api
```

This starts the FastAPI server over localhost on port 6900.

### Add to Workspace

See the documentation [here](https://docs.openbb.co/odp/python/quickstart/workspace) for more details. Once added, click an app to open its dashboard.

## Coverage

### Apps

- FOMC Documents
- Federal Reserve System - Stats & Indicators
- FFIEC & Bank Regulatory Data
- One app per regional Reserve Bank: Atlanta, Boston, Chicago, Cleveland, Dallas, Kansas City, Minneapolis, New York, Philadelphia, Richmond, San Francisco, and Saint Louis.

### Endpoints

All commands are exposed under the `.federal_reserve` namespace.

**Board statistics** — `.federal_reserve.*`

- fed_data, fomc_documents, inflation_expectations, international_portfolio_investment, list_datasets, list_releases, money_market_funds, money_measures, release_calendar, treasury_rates, yield_curve

**FFIEC & bank regulatory** — `.federal_reserve.ffiec.*`

- bhcpr_report, call_report, call_report_sectioned, country_exposure, custom_peer_group, executive_summary, financial_statements, institution_structure, institutions, large_holding_companies, list_of_banks_peer_group, peer_group_average, peer_group_bank, peer_group_distribution, state_average, systemic_risk, ubpr

**Regional Reserve Banks** — `.federal_reserve.<district>.*`

- `atlanta` — business_inflation_expectations, business_uncertainty, gdpnow, market_probability, publications, sticky_cpi, taylor_rule, taylor_rule_heatmap, taylor_rule_measures, wage_growth
- `boston` — economic_indicators, publications
- `chicago` — ag_credit_conditions, brave_butters_kelley, economic_conditions, farm_loan_rates, farmland_values, financial_conditions, labor_market, midwest_economy, national_activity, publications, retail_trade
- `cleveland` — inflation_expectations, inflation_nowcast, median_cpi, median_cpi_components, publications, systemic_risk
- `dallas` — agricultural_survey, banking_conditions, breakeven_prices, energy_survey, gigafactory_map, global_economic_indicators, global_real_economic_activity, government_debt, leading_index, lithium_map, manufacturing, publications, retail, service_sector, trimmed_mean_pce, weekly_economic_index
- `kc` — ag_credit_survey, ag_databook_archived, ag_district_surveys, ag_finance_databook, ag_interest_rates, ag_terms_of_lending, divisional_lmci, financial_stress_index, natural_rate, policy_rate_uncertainty, publications, risk_index
- `minneapolis` — business_conditions, job_openings_hiring, labor_force_participation, publications, quits_rate, regional_cpi, regional_employment, regional_gdp, regional_unemployment, unemployment_claims
- `ny` — business_leaders, central_bank_holdings, consumer_credit_access, consumer_expectations, consumer_housing, consumer_labor_market, core_trend_inflation, corporate_bond_distress, effr, empire_state_manufacturing, empire_state_reports, household_debt, market_expectations, overnight_bank_funding, primary_dealer_fails, primary_dealer_positioning, publications, sofr, supply_chain_pressure
- `philadelphia` — anxious_index, business_conditions, gdpplus, livingston_survey, manufacturing_outlook, nonmanufacturing_outlook, partisan_conflict, publications, state_coincident_index, survey_professional_forecasters, term_structure_inflation
- `richmond` — cfo_survey, manufacturing_survey, non_employment_index, recession_indicator, service_sector_survey, state_survey, survey_releases
- `sf` — cyclical_pce, news_sentiment, proxy_funds_rate, publications, short_rate_path, supply_demand_pce, term_premium, total_factor_productivity
- `stl` — fred_md, fred_qd, national_index, publications
