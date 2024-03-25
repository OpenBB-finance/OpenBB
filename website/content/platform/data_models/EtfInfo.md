---
title: "Etf Info"
description: "ETF Information Overview"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `EtfInfo` | `EtfInfoQueryParams` | `EtfInfoData` |

### Import Statement

```python
from openbb_core.provider.standard_models.etf_info import (
EtfInfoData,
EtfInfoQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) Multiple items allowed for provider(s): fmp, intrinio, tmx, yfinance. |  | False |
| provider | Literal['fmp', 'intrinio', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) Multiple items allowed for provider(s): fmp, intrinio, tmx, yfinance. |  | False |
| provider | Literal['fmp', 'intrinio', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) Multiple items allowed for provider(s): fmp, intrinio, tmx, yfinance. |  | False |
| provider | Literal['fmp', 'intrinio', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) Multiple items allowed for provider(s): fmp, intrinio, tmx, yfinance. |  | False |
| provider | Literal['fmp', 'intrinio', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| use_cache | bool | Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily. To bypass, set to False. If True, the data will be cached for 4 hours. | True | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) Multiple items allowed for provider(s): fmp, intrinio, tmx, yfinance. |  | False |
| provider | Literal['fmp', 'intrinio', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (ETF) |
| name | str | Name of the ETF. |
| description | str | Description of the fund. |
| inception_date | str | Inception date of the ETF. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (ETF) |
| name | str | Name of the ETF. |
| description | str | Description of the fund. |
| inception_date | str | Inception date of the ETF. |
| issuer | str | Company of the ETF. |
| cusip | str | CUSIP of the ETF. |
| isin | str | ISIN of the ETF. |
| domicile | str | Domicile of the ETF. |
| asset_class | str | Asset class of the ETF. |
| aum | float | Assets under management. |
| nav | float | Net asset value of the ETF. |
| nav_currency | str | Currency of the ETF's net asset value. |
| expense_ratio | float | The expense ratio, as a normalized percent. |
| holdings_count | int | Number of holdings. |
| avg_volume | float | Average daily trading volume. |
| website | str | Website of the issuer. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (ETF) |
| name | str | Name of the ETF. |
| description | str | Description of the fund. |
| inception_date | str | Inception date of the ETF. |
| fund_listing_date | date | The date on which the Exchange Traded Product (ETP) or share class of the ETP is listed on a specific exchange. |
| data_change_date | date | The last date on which there was a change in a classifications data field for this ETF. |
| etn_maturity_date | date | If the product is an ETN, this field identifies the maturity date for the ETN. |
| is_listed | bool | If true, the ETF is still listed on an exchange. |
| close_date | date | The date on which the ETF was de-listed if it is no longer listed. |
| exchange | str | The exchange Market Identifier Code (MIC). |
| isin | str | International Securities Identification Number (ISIN). |
| ric | str | Reuters Instrument Code (RIC). |
| sedol | str | Stock Exchange Daily Official List (SEDOL). |
| figi_symbol | str | Financial Instrument Global Identifier (FIGI) symbol. |
| share_class_figi | str | Financial Instrument Global Identifier (FIGI). |
| firstbridge_id | str | The FirstBridge unique identifier for the Exchange Traded Fund (ETF). |
| firstbridge_parent_id | str | The FirstBridge unique identifier for the parent Exchange Traded Fund (ETF), if applicable. |
| intrinio_id | str | Intrinio unique identifier for the security. |
| intraday_nav_symbol | str | Intraday Net Asset Value (NAV) symbol. |
| primary_symbol | str | The primary ticker field is used for Exchange Traded Products (ETPs) that have multiple listings and share classes. If an ETP has multiple listings or share classes, the same primary ticker is assigned to all the listings and share classes. |
| etp_structure_type | str | Classifies Exchange Traded Products (ETPs) into very broad categories based on its legal structure. |
| legal_structure | str | Legal structure of the fund. |
| issuer | str | Issuer of the ETF. |
| etn_issuing_bank | str | If the product is an Exchange Traded Note (ETN), this field identifies the issuing bank. |
| fund_family | str | This field identifies the fund family to which the ETF belongs, as categorized by the ETF Sponsor. |
| investment_style | str | Investment style of the ETF. |
| derivatives_based | str | This field is populated if the ETF holds either listed or over-the-counter derivatives in its portfolio. |
| income_category | str | Identifies if an Exchange Traded Fund (ETF) falls into a category that is specifically designed to provide a high yield or income |
| asset_class | str | Captures the underlying nature of the securities in the Exchanged Traded Product (ETP). |
| other_asset_types | str | If 'asset_class' field is classified as 'Other Asset Types' this field captures the specific category of the underlying assets. |
| single_category_designation | str | This categorization is created for those users who want every ETF to be 'forced' into a single bucket, so that the assets for all categories will always sum to the total market. |
| beta_type | str | This field identifies whether an ETF provides 'Traditional' beta exposure or 'Smart' beta exposure. ETFs that are active (i.e. non-indexed), leveraged / inverse or have a proprietary quant model (i.e. that don't provide indexed exposure to a targeted factor) are classified separately. |
| beta_details | str | This field provides further detail within the traditional and smart beta categories. |
| market_cap_range | str | Equity ETFs are classified as falling into categories based on the description of their investment strategy in the prospectus. Examples ('Mega Cap', 'Large Cap', 'Mid Cap', etc.) |
| market_cap_weighting_type | str | For ETFs that take the value 'Market Cap Weighted' in the 'index_weighting_scheme' field, this field provides detail on the market cap weighting type. |
| index_weighting_scheme | str | For ETFs that track an underlying index, this field provides detail on the index weighting type. |
| index_linked | str | This field identifies whether an ETF is index linked or active. |
| index_name | str | This field identifies the name of the underlying index tracked by the ETF, if applicable. |
| index_symbol | str | This field identifies the OpenFIGI ticker for the Index underlying the ETF. |
| parent_index | str | This field identifies the name of the parent index, which represents the broader universe from which the index underlying the ETF is created, if applicable. |
| index_family | str | This field identifies the index family to which the index underlying the ETF belongs. The index family is represented as categorized by the index provider. |
| broader_index_family | str | This field identifies the broader index family to which the index underlying the ETF belongs. The broader index family is represented as categorized by the index provider. |
| index_provider | str | This field identifies the Index provider for the index underlying the ETF, if applicable. |
| index_provider_code | str | This field provides the First Bridge code for each Index provider, corresponding to the index underlying the ETF if applicable. |
| replication_structure | str | The replication structure of the Exchange Traded Product (ETP). |
| growth_value_tilt | str | Classifies equity ETFs as either 'Growth' or Value' based on the stated style tilt in the ETF prospectus. Equity ETFs that do not have a stated style tilt are classified as 'Core / Blend'. |
| growth_type | str | For ETFs that are classified as 'Growth' in 'growth_value_tilt', this field further identifies those where the stocks in the ETF are both selected and weighted based on their growth (style factor) scores. |
| value_type | str | For ETFs that are classified as 'Value' in 'growth_value_tilt', this field further identifies those where the stocks in the ETF are both selected and weighted based on their value (style factor) scores. |
| sector | str | For equity ETFs that aim to provide targeted exposure to a sector or industry, this field identifies the Sector that it provides the exposure to. |
| industry | str | For equity ETFs that aim to provide targeted exposure to an industry, this field identifies the Industry that it provides the exposure to. |
| industry_group | str | For equity ETFs that aim to provide targeted exposure to a sub-industry, this field identifies the sub-Industry that it provides the exposure to. |
| cross_sector_theme | str | For equity ETFs that aim to provide targeted exposure to a specific investment theme that cuts across GICS sectors, this field identifies the specific cross-sector theme. Examples ('Agri-business', 'Natural Resources', 'Green Investing', etc.) |
| natural_resources_type | str | For ETFs that are classified as 'Natural Resources' in the 'cross_sector_theme' field, this field provides further detail on the type of Natural Resources exposure. |
| us_or_excludes_us | str | Takes the value of 'Domestic' for US exposure, 'International' for non-US exposure and 'Global' for exposure that includes all regions including the US. |
| developed_emerging | str | This field identifies the stage of development of the markets that the ETF provides exposure to. |
| specialized_region | str | This field is populated if the ETF provides targeted exposure to a specific type of geography-based grouping that does not fall into a specific country or continent grouping. Examples ('BRIC', 'Chindia', etc.) |
| continent | str | This field is populated if the ETF provides targeted exposure to a specific continent or country within that Continent. |
| latin_america_sub_group | str | For ETFs that are classified as 'Latin America' in the 'continent' field, this field provides further detail on the type of regional exposure. |
| europe_sub_group | str | For ETFs that are classified as 'Europe' in the 'continent' field, this field provides further detail on the type of regional exposure. |
| asia_sub_group | str | For ETFs that are classified as 'Asia' in the 'continent' field, this field provides further detail on the type of regional exposure. |
| specific_country | str | This field is populated if the ETF provides targeted exposure to a specific country. |
| china_listing_location | str | For ETFs that are classified as 'China' in the 'country' field, this field provides further detail on the type of exposure in the underlying securities. |
| us_state | str | Takes the value of a US state if the ETF provides targeted exposure to the municipal bonds or equities of companies. |
| real_estate | str | For ETFs that provide targeted real estate exposure, this field is populated if the ETF provides targeted exposure to a specific segment of the real estate market. |
| fundamental_weighting_type | str | For ETFs that take the value 'Fundamental Weighted' in the 'index_weighting_scheme' field, this field provides detail on the fundamental weighting methodology. |
| dividend_weighting_type | str | For ETFs that take the value 'Dividend Weighted' in the 'index_weighting_scheme' field, this field provides detail on the dividend weighting methodology. |
| bond_type | str | For ETFs where 'asset_class_type' is 'Bonds', this field provides detail on the type of bonds held in the ETF. |
| government_bond_types | str | For bond ETFs that take the value 'Treasury & Government' in 'bond_type', this field provides detail on the exposure. |
| municipal_bond_region | str | For bond ETFs that take the value 'Municipal' in 'bond_type', this field provides additional detail on the geographic exposure. |
| municipal_vrdo | bool | For bond ETFs that take the value 'Municipal' in 'bond_type', this field identifies those ETFs that specifically provide exposure to Variable Rate Demand Obligations. |
| mortgage_bond_types | str | For bond ETFs that take the value 'Mortgage' in 'bond_type', this field provides additional detail on the type of underlying securities. |
| bond_tax_status | str | For all US bond ETFs, this field provides additional detail on the tax treatment of the underlying securities. |
| credit_quality | str | For all bond ETFs, this field helps to identify if the ETF provides targeted exposure to securities of a specific credit quality range. |
| average_maturity | str | For all bond ETFs, this field helps to identify if the ETF provides targeted exposure to securities of a specific maturity range. |
| specific_maturity_year | int | For all bond ETFs that take the value 'Specific Maturity Year' in the 'average_maturity' field, this field specifies the calendar year. |
| commodity_types | str | For ETFs where 'asset_class_type' is 'Commodities', this field provides detail on the type of commodities held in the ETF. |
| energy_type | str | For ETFs where 'commodity_type' is 'Energy', this field provides detail on the type of energy exposure provided by the ETF. |
| agricultural_type | str | For ETFs where 'commodity_type' is 'Agricultural', this field provides detail on the type of agricultural exposure provided by the ETF. |
| livestock_type | str | For ETFs where 'commodity_type' is 'Livestock', this field provides detail on the type of livestock exposure provided by the ETF. |
| metal_type | str | For ETFs where 'commodity_type' is 'Gold & Metals', this field provides detail on the type of exposure provided by the ETF. |
| inverse_leveraged | str | This field is populated if the ETF provides inverse or leveraged exposure. |
| target_date_multi_asset_type | str | For ETFs where 'asset_class_type' is 'Target Date / MultiAsset', this field provides detail on the type of commodities held in the ETF. |
| currency_pair | str | This field is populated if the ETF's strategy involves providing exposure to the movements of a currency or involves hedging currency exposure. |
| social_environmental_type | str | This field is populated if the ETF's strategy involves providing exposure to a specific social or environmental theme. |
| clean_energy_type | str | This field is populated if the ETF has a value of 'Clean Energy' in the 'social_environmental_type' field. |
| dividend_type | str | This field is populated if the ETF has an intended investment objective of holding dividend-oriented stocks as stated in the prospectus. |
| regular_dividend_payor_type | str | This field is populated if the ETF has a value of'Dividend - Regular Payors' in the 'dividend_type' field. |
| quant_strategies_type | str | This field is populated if the ETF has either an index-linked or active strategy that is based on a proprietary quantitative strategy. |
| other_quant_models | str | For ETFs where 'quant_strategies_type' is 'Other Quant Model', this field provides the name of the specific proprietary quant model used as the underlying strategy for the ETF. |
| hedge_fund_type | str | For ETFs where 'other_asset_types' is 'Hedge Fund Replication', this field provides detail on the type of hedge fund replication strategy. |
| excludes_financials | bool | For equity ETFs, identifies those ETFs where the underlying fund holdings will not hold financials stocks, based on the funds intended objective. |
| excludes_technology | bool | For equity ETFs, identifies those ETFs where the underlying fund holdings will not hold technology stocks, based on the funds intended objective. |
| holds_only_nyse_stocks | bool | If true, the ETF is an equity ETF and holds only stocks listed on NYSE. |
| holds_only_nasdaq_stocks | bool | If true, the ETF is an equity ETF and holds only stocks listed on Nasdaq. |
| holds_mlp | bool | If true, the ETF's investment objective explicitly specifies that it holds MLPs as an intended part of its investment strategy. |
| holds_preferred_stock | bool | If true, the ETF's investment objective explicitly specifies that it holds preferred stock as an intended part of its investment strategy. |
| holds_closed_end_funds | bool | If true, the ETF's investment objective explicitly specifies that it holds closed end funds as an intended part of its investment strategy. |
| holds_adr | bool | If true, he ETF's investment objective explicitly specifies that it holds American Depositary Receipts (ADRs) as an intended part of its investment strategy. |
| laddered | bool | For bond ETFs, this field identifies those ETFs that specifically hold bonds in a laddered structure, where the bonds are scheduled to mature in an annual, sequential structure. |
| zero_coupon | bool | For bond ETFs, this field identifies those ETFs that specifically hold zero coupon Treasury Bills. |
| floating_rate | bool | For bond ETFs, this field identifies those ETFs that specifically hold floating rate bonds. |
| build_america_bonds | bool | For municipal bond ETFs, this field identifies those ETFs that specifically hold Build America Bonds. |
| dynamic_futures_roll | bool | If the product holds futures contracts, this field identifies those products where the roll strategy is dynamic (rather than entirely rules based), so as to minimize roll costs. |
| currency_hedged | bool | This field is populated if the ETF's strategy involves hedging currency exposure. |
| includes_short_exposure | bool | This field is populated if the ETF has short exposure in any of its holdings e.g. in a long/short or inverse ETF. |
| ucits | bool | If true, the Exchange Traded Product (ETP) is Undertakings for the Collective Investment in Transferable Securities (UCITS) compliant |
| registered_countries | str | The list of countries where the ETF is legally registered for sale. This may differ from where the ETF is domiciled or traded, particularly in Europe. |
| issuer_country | str | 2 letter ISO country code for the country where the issuer is located. |
| domicile | str | 2 letter ISO country code for the country where the ETP is domiciled. |
| listing_country | str | 2 letter ISO country code for the country of the primary listing. |
| listing_region | str | Geographic region in the country of the primary listing falls. |
| bond_currency_denomination | str | For all bond ETFs, this field provides additional detail on the currency denomination of the underlying securities. |
| base_currency | str | Base currency in which NAV is reported. |
| listing_currency | str | Listing currency of the Exchange Traded Product (ETP) in which it is traded. Reported using the 3-digit ISO currency code. |
| number_of_holdings | int | The number of holdings in the ETF. |
| month_end_assets | float | Net assets in millions of dollars as of the most recent month end. |
| net_expense_ratio | float | Gross expense net of Fee Waivers, as a percentage of net assets as published by the ETF issuer. |
| etf_portfolio_turnover | float | The percentage of positions turned over in the last 12 months. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (ETF) |
| name | str | Name of the ETF. |
| description | str | Description of the fund. |
| inception_date | str | Inception date of the ETF. |
| issuer | str | The issuer of the ETF. |
| investment_style | str | The investment style of the ETF. |
| esg | bool | Whether the ETF qualifies as an ESG fund. |
| currency | str | The currency of the ETF. |
| unit_price | float | The unit price of the ETF. |
| close | float | The closing price of the ETF. |
| prev_close | float | The previous closing price of the ETF. |
| return_1m | float | The one-month return of the ETF, as a normalized percent |
| return_3m | float | The three-month return of the ETF, as a normalized percent. |
| return_6m | float | The six-month return of the ETF, as a normalized percent. |
| return_ytd | float | The year-to-date return of the ETF, as a normalized percent. |
| return_1y | float | The one-year return of the ETF, as a normalized percent. |
| return_3y | float | The three-year return of the ETF, as a normalized percent. |
| return_5y | float | The five-year return of the ETF, as a normalized percent. |
| return_10y | float | The ten-year return of the ETF, as a normalized percent. |
| return_from_inception | float | The return from inception of the ETF, as a normalized percent. |
| avg_volume | int | The average daily volume of the ETF. |
| avg_volume_30d | int | The 30-day average volume of the ETF. |
| aum | float | The AUM of the ETF. |
| pe_ratio | float | The price-to-earnings ratio of the ETF. |
| pb_ratio | float | The price-to-book ratio of the ETF. |
| management_fee | float | The management fee of the ETF, as a normalized percent. |
| mer | float | The management expense ratio of the ETF, as a normalized percent. |
| distribution_yield | float | The distribution yield of the ETF, as a normalized percent. |
| dividend_frequency | str | The dividend payment frequency of the ETF. |
| website | str | The website of the ETF. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (ETF) |
| name | str | Name of the ETF. |
| description | str | Description of the fund. |
| inception_date | str | Inception date of the ETF. |
| fund_type | str | The legal type of fund. |
| fund_family | str | The fund family. |
| category | str | The fund category. |
| exchange | str | The exchange the fund is listed on. |
| exchange_timezone | str | The timezone of the exchange. |
| currency | str | The currency in which the fund is listed. |
| nav_price | float | The net asset value per unit of the fund. |
| total_assets | int | The total value of assets held by the fund. |
| trailing_pe | float | The trailing twelve month P/E ratio of the fund's assets. |
| dividend_yield | float | The dividend yield of the fund, as a normalized percent. |
| dividend_rate_ttm | float | The trailing twelve month annual dividend rate of the fund, in currency units. |
| dividend_yield_ttm | float | The trailing twelve month annual dividend yield of the fund, as a normalized percent. |
| year_high | float | The fifty-two week high price. |
| year_low | float | The fifty-two week low price. |
| ma_50d | float | 50-day moving average price. |
| ma_200d | float | 200-day moving average price. |
| return_ytd | float | The year-to-date return of the fund, as a normalized percent. |
| return_3y_avg | float | The three year average return of the fund, as a normalized percent. |
| return_5y_avg | float | The five year average return of the fund, as a normalized percent. |
| beta_3y_avg | float | The three year average beta of the fund. |
| volume_avg | float | The average daily trading volume of the fund. |
| volume_avg_10d | float | The average daily trading volume of the fund over the past ten days. |
| bid | float | The current bid price. |
| bid_size | float | The current bid size. |
| ask | float | The current ask price. |
| ask_size | float | The current ask size. |
| open | float | The open price of the most recent trading session. |
| high | float | The highest price of the most recent trading session. |
| low | float | The lowest price of the most recent trading session. |
| volume | int | The trading volume of the most recent trading session. |
| prev_close | float | The previous closing price. |
</TabItem>

</Tabs>

