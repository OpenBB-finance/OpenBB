---
title: search
description: The 'search' documentation provides a detailed guide to using various
  search commands on our platform. This includes usage, parameters, and term definitions
  for finding company tickers, filtering stocks based on country, sector, industry
  or specific exchange country.
keywords:
- Search Documentation
- Company Tickers
- Stock Market Search
- Search By Country
- Search By Sector
- Search By Industry
- Search By Exchange Country
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /search - Reference | OpenBB Terminal Docs" />

Show companies matching the search query, country, sector, industry and/or exchange. Note that by default only the United States exchanges are searched which tend to contain the most extensive data for each company. To search all exchanges use the --all-exchanges flag.

### Usage

```python wordwrap
search [-q QUERY [QUERY ...]] [-c country] [-s sector] [--industrygroup industry_group] [-i industry] [-e exchange] [--exchangecountry exchange_country] [-a]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| query | -q  --query | The search term used to find company tickers |  | True | None |
| country | -c  --country | Search by country to find stocks matching the criteria |  | True | afghanistan, anguilla, argentina, australia, austria, azerbaijan, bahamas, bangladesh, barbados, belgium, belize, bermuda, botswana, brazil, british_virgin_islands, cambodia, canada, cayman_islands, chile, china, colombia, costa_rica, cyprus, czech_republic, denmark, dominican_republic, egypt, estonia, falkland_islands, finland, france, french_guiana, gabon, georgia, germany, ghana, gibraltar, greece, greenland, guernsey, hong_kong, hungary, iceland, india, indonesia, ireland, isle_of_man, israel, italy, ivory_coast, japan, jersey, jordan, kazakhstan, kenya, kyrgyzstan, latvia, liechtenstein, lithuania, luxembourg, macau, macedonia, malaysia, malta, mauritius, mexico, monaco, mongolia, montenegro, morocco, mozambique, myanmar, namibia, netherlands, netherlands_antilles, new_zealand, nigeria, norway, panama, papua_new_guinea, peru, philippines, poland, portugal, qatar, reunion, romania, russia, saudi_arabia, senegal, singapore, slovakia, slovenia, south_africa, south_korea, spain, suriname, sweden, switzerland, taiwan, tanzania, thailand, turkey, ukraine, united_arab_emirates, united_kingdom, united_states, uruguay, vietnam, zambia |
| sector | -s  --sector | Search by sector to find stocks matching the criteria |  | True | communication_services, consumer_discretionary, consumer_staples, energy, financials, health_care, industrials, information_technology, materials, real_estate, utilities |
| industry_group | --industrygroup | Search by industry group to find stocks matching the criteria |  | True | automobiles_&_components, banks, capital_goods, commercial_&_professional_services, consumer_durables_&_apparel, consumer_services, diversified_financials, energy, food_&_staples_retailing, food,_beverage_&_tobacco, health_care_equipment_&_services, household_&_personal_products, insurance, materials, media_&_entertainment, pharmaceuticals,_biotechnology_&_life_sciences, real_estate, retailing, semiconductors_&_semiconductor_equipment, software_&_services, technology_hardware_&_equipment, telecommunication_services, transportation, utilities |
| industry | -i  --industry | Search by industry to find stocks matching the criteria |  | True | aerospace_&_defense, air_freight_&_logistics, airlines, auto_components, automobiles, banks, beverages, biotechnology, building_products, capital_markets, chemicals, commercial_services_&_supplies, communications_equipment, construction_&_engineering, construction_materials, consumer_finance, distributors, diversified_consumer_services, diversified_financial_services, diversified_telecommunication_services, electric_utilities, electrical_equipment, electronic_equipment,_instruments_&_components, energy_equipment_&_services, entertainment, equity_real_estate_investment_trusts_(reits), food_&_staples_retailing, food_products, gas_utilities, health_care_equipment_&_supplies, health_care_providers_&_services, health_care_technology, hotels,_restaurants_&_leisure, household_durables, household_products, it_services, independent_power_and_renewable_electricity_producers, industrial_conglomerates, insurance, interactive_media_&_services, internet_&_direct_marketing_retail, machinery, marine, media, metals_&_mining, multi-utilities, oil,_gas_&_consumable_fuels, paper_&_forest_products, pharmaceuticals, professional_services, real_estate_management_&_development, road_&_rail, semiconductors_&_semiconductor_equipment, software, specialty_retail, technology_hardware,_storage_&_peripherals, textiles,_apparel_&_luxury_goods, thrifts_&_mortgage_finance, tobacco, trading_companies_&_distributors, transportation_infrastructure, water_utilities |
| exchange | -e  --exchange | Search by a specific exchange to find stocks matching the criteria |  | True | ams, aqs, ase, asx, ath, ber, bru, bse, bts, bud, bue, cai, ccs, cnq, cph, cse, doh, dus, ebs, enx, fka, fra, ger, ham, han, hel, hkg, ice, iob, ise, ist, jkt, jnb, jpx, kls, koe, ksc, lis, lit, lse, mce, mcx, mex, mil, mun, nae, nas, ncm, neo, ngm, nms, nse, nsi, nyq, nys, nze, obb, osl, par, pcx, pnk, pra, ris, sao, sap, sat, sau, ses, set, sgo, shh, shz, sto, stu, tai, tal, tlo, tlv, tor, two, van, vie |
| exchange_country | --exchangecountry | Search by a specific country and all its exchanges to find stocks matching the criteria |  | True | united_states, argentina, austria, australia, belgium, brazil, canada, chile, china, czech_republic, denmark, egypt, estonia, europe, finland, france, germany, greece, hong_kong, hungary, iceland, india, indonesia, ireland, israel, italy, japan, latvia, lithuania, malaysia, mexico, netherlands, new_zealand, norway, portugal, qatar, russia, singapore, south_africa, south_korea, spain, saudi_arabia, sweden, switzerland, taiwan, thailand, turkey, united_kingdom, venezuela |
| all_exchanges | -a  --all-exchanges | Whether to search all exchanges, without this option only the United States market is searched. | False | True | None |

---
