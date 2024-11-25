"""Intrinio ETF Info Model."""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_requests
from pydantic import Field


class IntrinioEtfInfoQueryParams(EtfInfoQueryParams):
    """
    Intrinio ETF Info Query Params.

    Source: https://docs.intrinio.com/documentation/web_api/get_etf_v2
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class IntrinioEtfInfoData(EtfInfoData):
    """Intrinio ETF Info Data."""

    __alias_dict__ = {
        "symbol": "ticker",
        "exchange": "exchange_mic",
        "issuer": "sponsor",
        "investment_style": "type",
        "industry_group": "sub_industry",
        "holds_mlp": "holds_ml_ps",
        "holds_adr": "holds_ad_rs",
        "index_symbol": "index_ticker",
        "figi_symbol": "figi_ticker",
        "intrinio_id": "id",
        "is_listed": "is_live_listed",
        "beta_type": "smartvs_traditional_beta",
        "beta_details": "smartvs_traditional_beta_level2",
        "listing_country": "primary_ticker_country_code",
        "listing_region": "primary_listing_region",
        "primary_symbol": "primary_ticker",
        "intraday_nav_symbol": "intraday_nav_ticker",
        "issuer_country": "issuing_entity_country_code",
        "livestock_type": "livestock",
    }

    fund_listing_date: Optional[dateType] = Field(
        default=None,
        description="The date on which the Exchange Traded Product (ETP)"
        + " or share class of the ETP is listed on a specific exchange.",
    )
    data_change_date: Optional[dateType] = Field(
        default=None,
        description="The last date on which there was a change in a classifications data field for this ETF.",
    )
    etn_maturity_date: Optional[dateType] = Field(
        default=None,
        description="If the product is an ETN, this field identifies the maturity date for the ETN.",
    )
    is_listed: Optional[bool] = Field(
        default=None,
        description="If true, the ETF is still listed on an exchange.",
    )
    close_date: Optional[dateType] = Field(
        default=None,
        description="The date on which the ETF was de-listed if it is no longer listed.",
    )
    exchange: Optional[str] = Field(
        default=None,
        description="The exchange Market Identifier Code (MIC).",
    )
    isin: Optional[str] = Field(
        default=None,
        description="International Securities Identification Number (ISIN).",
    )
    ric: Optional[str] = Field(
        default=None,
        description="Reuters Instrument Code (RIC).",
    )
    sedol: Optional[str] = Field(
        default=None,
        description="Stock Exchange Daily Official List (SEDOL).",
    )
    figi_symbol: Optional[str] = Field(
        default=None,
        description="Financial Instrument Global Identifier (FIGI) symbol.",
    )
    share_class_figi: Optional[str] = Field(
        default=None,
        description="Financial Instrument Global Identifier (FIGI).",
    )
    firstbridge_id: Optional[str] = Field(
        default=None,
        description="The FirstBridge unique identifier for the Exchange Traded Fund (ETF).",
    )
    firstbridge_parent_id: Optional[str] = Field(
        default=None,
        description="The FirstBridge unique identifier for the parent Exchange Traded Fund (ETF), if applicable.",
    )
    intrinio_id: Optional[str] = Field(
        default=None,
        description="Intrinio unique identifier for the security.",
    )
    intraday_nav_symbol: Optional[str] = Field(
        default=None,
        description="Intraday Net Asset Value (NAV) symbol.",
    )
    primary_symbol: Optional[str] = Field(
        default=None,
        description="The primary ticker field is used for Exchange Traded Products (ETPs)"
        + " that have multiple listings and share classes."
        + " If an ETP has multiple listings or share classes,"
        + " the same primary ticker is assigned to all the listings and share classes.",
    )
    etp_structure_type: Optional[str] = Field(
        default=None,
        description="Classifies Exchange Traded Products (ETPs) into very broad categories based on its legal structure.",
    )
    legal_structure: Optional[str] = Field(
        default=None,
        description="Legal structure of the fund.",
    )
    issuer: Optional[str] = Field(
        default=None,
        description="Issuer of the ETF.",
    )
    etn_issuing_bank: Optional[str] = Field(
        default=None,
        description="If the product is an Exchange Traded Note (ETN), this field identifies the issuing bank.",
    )
    fund_family: Optional[str] = Field(
        default=None,
        description="This field identifies the fund family to which the ETF belongs, as categorized by the ETF Sponsor.",
    )
    investment_style: Optional[str] = Field(
        default=None,
        description="Investment style of the ETF.",
    )
    derivatives_based: Optional[str] = Field(
        default=None,
        description="This field is populated if the ETF holds either"
        + " listed or over-the-counter derivatives in its portfolio.",
    )
    income_category: Optional[str] = Field(
        default=None,
        description="Identifies if an Exchange Traded Fund (ETF) falls into a category"
        + " that is specifically designed to provide a high yield or income",
    )
    asset_class: Optional[str] = Field(
        default=None,
        description="Captures the underlying nature of the securities in the Exchanged Traded Product (ETP).",
    )
    other_asset_types: Optional[str] = Field(
        default=None,
        description="If 'asset_class' field is classified as 'Other Asset Types'"
        + " this field captures the specific category of the underlying assets.",
    )
    single_category_designation: Optional[str] = Field(
        default=None,
        description="This categorization is created for those users who want every ETF to be 'forced'"
        + " into a single bucket, so that the assets for all categories will always sum to the total market.",
    )
    beta_type: Optional[str] = Field(
        default=None,
        description="This field identifies whether an ETF provides 'Traditional' beta exposure or 'Smart' beta exposure."
        + " ETFs that are active (i.e. non-indexed), leveraged / inverse or have a proprietary quant model"
        + " (i.e. that don't provide indexed exposure to a targeted factor) are classified separately.",
    )
    beta_details: Optional[str] = Field(
        default=None,
        description="This field provides further detail within the traditional and smart beta categories.",
    )
    market_cap_range: Optional[str] = Field(
        default=None,
        description="Equity ETFs are classified as falling into categories"
        + " based on the description of their investment strategy in the prospectus."
        + " Examples ('Mega Cap', 'Large Cap', 'Mid Cap', etc.)",
    )
    market_cap_weighting_type: Optional[str] = Field(
        default=None,
        description="For ETFs that take the value 'Market Cap Weighted' in the 'index_weighting_scheme' field,"
        + " this field provides detail on the market cap weighting type.",
    )
    index_weighting_scheme: Optional[str] = Field(
        default=None,
        description="For ETFs that track an underlying index,"
        + " this field provides detail on the index weighting type.",
    )
    index_linked: Optional[str] = Field(
        default=None,
        description="This field identifies whether an ETF is index linked or active.",
    )
    index_name: Optional[str] = Field(
        default=None,
        description="This field identifies the name of the underlying index tracked by the ETF, if applicable.",
    )
    index_symbol: Optional[str] = Field(
        default=None,
        description="This field identifies the OpenFIGI ticker for the Index underlying the ETF.",
    )
    parent_index: Optional[str] = Field(
        default=None,
        description="This field identifies the name of the parent index, which represents"
        + " the broader universe from which the index underlying the ETF is created, if applicable.",
    )
    index_family: Optional[str] = Field(
        default=None,
        description="This field identifies the index family to which the index underlying the ETF belongs."
        + " The index family is represented as categorized by the index provider.",
    )
    broader_index_family: Optional[str] = Field(
        default=None,
        description="This field identifies the broader index family to which the index underlying the ETF belongs."
        + " The broader index family is represented as categorized by the index provider.",
    )
    index_provider: Optional[str] = Field(
        default=None,
        description="This field identifies the Index provider for the index underlying the ETF, if applicable.",
    )
    index_provider_code: Optional[str] = Field(
        default=None,
        description="This field provides the First Bridge code for each Index provider,"
        + " corresponding to the index underlying the ETF if applicable.",
    )
    replication_structure: Optional[str] = Field(
        default=None,
        description="The replication structure of the Exchange Traded Product (ETP).",
    )
    growth_value_tilt: Optional[str] = Field(
        default=None,
        description="Classifies equity ETFs as either 'Growth' or Value' based on the stated style tilt"
        + " in the ETF prospectus. Equity ETFs that do not have a stated style tilt are classified as 'Core / Blend'.",
    )
    growth_type: Optional[str] = Field(
        default=None,
        description="For ETFs that are classified as 'Growth' in 'growth_value_tilt',"
        + " this field further identifies those where the stocks in the"
        + " ETF are both selected and weighted based on their growth (style factor) scores.",
    )
    value_type: Optional[str] = Field(
        default=None,
        description="For ETFs that are classified as 'Value' in 'growth_value_tilt',"
        + " this field further identifies those where the stocks in the"
        + " ETF are both selected and weighted based on their value (style factor) scores.",
    )
    sector: Optional[str] = Field(
        default=None,
        description="For equity ETFs that aim to provide targeted exposure to a sector or industry,"
        + " this field identifies the Sector that it provides the exposure to.",
    )
    industry: Optional[str] = Field(
        default=None,
        description="For equity ETFs that aim to provide targeted exposure to an industry,"
        + " this field identifies the Industry that it provides the exposure to.",
    )
    industry_group: Optional[str] = Field(
        default=None,
        description="For equity ETFs that aim to provide targeted exposure to a sub-industry,"
        + " this field identifies the sub-Industry that it provides the exposure to.",
    )
    cross_sector_theme: Optional[str] = Field(
        default=None,
        description="For equity ETFs that aim to provide targeted exposure to a specific investment theme"
        + " that cuts across GICS sectors, this field identifies the specific cross-sector theme."
        + " Examples ('Agri-business', 'Natural Resources', 'Green Investing', etc.)",
    )
    natural_resources_type: Optional[str] = Field(
        default=None,
        description="For ETFs that are classified as 'Natural Resources' in the 'cross_sector_theme' field,"
        + " this field provides further detail on the type of Natural Resources exposure.",
    )
    us_or_excludes_us: Optional[str] = Field(
        default=None,
        description="Takes the value of 'Domestic' for US exposure,"
        + " 'International' for non-US exposure and 'Global' for exposure that includes all regions including the US.",
    )
    developed_emerging: Optional[str] = Field(
        default=None,
        description="This field identifies the stage of development of the markets that the ETF provides exposure to.",
    )
    specialized_region: Optional[str] = Field(
        default=None,
        description="This field is populated if the ETF provides targeted"
        + " exposure to a specific type of geography-based grouping"
        + " that does not fall into a specific country or continent grouping."
        + " Examples ('BRIC', 'Chindia', etc.)",
    )
    continent: Optional[str] = Field(
        default=None,
        description="This field is populated if the ETF provides targeted exposure"
        + " to a specific continent or country within that Continent.",
    )
    latin_america_sub_group: Optional[str] = Field(
        default=None,
        description="For ETFs that are classified as 'Latin America' in the 'continent' field,"
        + " this field provides further detail on the type of regional exposure.",
    )
    europe_sub_group: Optional[str] = Field(
        default=None,
        description="For ETFs that are classified as 'Europe' in the 'continent' field,"
        + " this field provides further detail on the type of regional exposure.",
    )
    asia_sub_group: Optional[str] = Field(
        default=None,
        description="For ETFs that are classified as 'Asia' in the 'continent' field,"
        + " this field provides further detail on the type of regional exposure.",
    )
    specific_country: Optional[str] = Field(
        default=None,
        description="This field is populated if the ETF provides targeted exposure to a specific country.",
    )
    china_listing_location: Optional[str] = Field(
        default=None,
        description="For ETFs that are classified as 'China' in the 'country' field,"
        + " this field provides further detail on the type of exposure in the underlying securities.",
    )
    us_state: Optional[str] = Field(
        default=None,
        description="Takes the value of a US state if the ETF provides"
        + " targeted exposure to the municipal bonds or equities of companies.",
    )
    real_estate: Optional[str] = Field(
        default=None,
        description="For ETFs that provide targeted real estate exposure,"
        + " this field is populated if the ETF provides targeted"
        + " exposure to a specific segment of the real estate market.",
    )

    fundamental_weighting_type: Optional[str] = Field(
        default=None,
        description="For ETFs that take the value 'Fundamental Weighted' in the 'index_weighting_scheme' field,"
        + " this field provides detail on the fundamental weighting methodology.",
    )
    dividend_weighting_type: Optional[str] = Field(
        default=None,
        description="For ETFs that take the value 'Dividend Weighted' in the 'index_weighting_scheme' field,"
        + " this field provides detail on the dividend weighting methodology.",
    )
    bond_type: Optional[str] = Field(
        default=None,
        description="For ETFs where 'asset_class_type' is 'Bonds',"
        + " this field provides detail on the type of bonds held in the ETF.",
    )
    government_bond_types: Optional[str] = Field(
        default=None,
        description="For bond ETFs that take the value 'Treasury & Government' in 'bond_type',"
        + " this field provides detail on the exposure.",
    )
    municipal_bond_region: Optional[str] = Field(
        default=None,
        description="For bond ETFs that take the value 'Municipal' in 'bond_type',"
        + " this field provides additional detail on the geographic exposure.",
    )
    municipal_vrdo: Optional[bool] = Field(
        default=None,
        description="For bond ETFs that take the value 'Municipal' in 'bond_type',"
        + " this field identifies those ETFs that specifically provide exposure to Variable Rate Demand Obligations.",
    )
    mortgage_bond_types: Optional[str] = Field(
        default=None,
        description="For bond ETFs that take the value 'Mortgage' in 'bond_type',"
        + " this field provides additional detail on the type of underlying securities.",
    )
    bond_tax_status: Optional[str] = Field(
        default=None,
        description="For all US bond ETFs, this field provides additional"
        + " detail on the tax treatment of the underlying securities.",
    )
    credit_quality: Optional[str] = Field(
        default=None,
        description="For all bond ETFs, this field helps to identify if the ETF"
        + " provides targeted exposure to securities of a specific credit quality range.",
    )
    average_maturity: Optional[str] = Field(
        default=None,
        description="For all bond ETFs, this field helps to identify if the ETF"
        + " provides targeted exposure to securities of a specific maturity range.",
    )
    specific_maturity_year: Optional[int] = Field(
        default=None,
        description="For all bond ETFs that take the value 'Specific Maturity Year' in the 'average_maturity' field,"
        + " this field specifies the calendar year.",
    )
    commodity_types: Optional[str] = Field(
        default=None,
        description="For ETFs where 'asset_class_type' is 'Commodities',"
        + " this field provides detail on the type of commodities held in the ETF.",
    )
    energy_type: Optional[str] = Field(
        default=None,
        description="For ETFs where 'commodity_type' is 'Energy',"
        + " this field provides detail on the type of energy exposure provided by the ETF.",
    )
    agricultural_type: Optional[str] = Field(
        default=None,
        description="For ETFs where 'commodity_type' is 'Agricultural',"
        + " this field provides detail on the type of agricultural exposure provided by the ETF.",
    )
    livestock_type: Optional[str] = Field(
        default=None,
        description="For ETFs where 'commodity_type' is 'Livestock',"
        + " this field provides detail on the type of livestock exposure provided by the ETF.",
    )
    metal_type: Optional[str] = Field(
        default=None,
        description="For ETFs where 'commodity_type' is 'Gold & Metals',"
        + " this field provides detail on the type of exposure provided by the ETF.",
    )
    inverse_leveraged: Optional[str] = Field(
        default=None,
        description="This field is populated if the ETF provides inverse or leveraged exposure.",
    )
    target_date_multi_asset_type: Optional[str] = Field(
        default=None,
        description="For ETFs where 'asset_class_type' is 'Target Date / MultiAsset',"
        + " this field provides detail on the type of commodities held in the ETF.",
    )
    currency_pair: Optional[str] = Field(
        default=None,
        description="This field is populated if the ETF's strategy involves providing exposure to"
        + " the movements of a currency or involves hedging currency exposure.",
    )
    social_environmental_type: Optional[str] = Field(
        default=None,
        description="This field is populated if the ETF's strategy involves providing"
        + " exposure to a specific social or environmental theme.",
    )
    clean_energy_type: Optional[str] = Field(
        default=None,
        description="This field is populated if the ETF has a value of 'Clean Energy'"
        + " in the 'social_environmental_type' field.",
    )
    dividend_type: Optional[str] = Field(
        default=None,
        description="This field is populated if the ETF has an intended"
        + " investment objective of holding dividend-oriented stocks as stated in the prospectus.",
    )
    regular_dividend_payor_type: Optional[str] = Field(
        default=None,
        description="This field is populated if the ETF has a value of"
        + "'Dividend - Regular Payors' in the 'dividend_type' field.",
    )
    quant_strategies_type: Optional[str] = Field(
        default=None,
        description="This field is populated if the ETF has either an index-linked"
        + " or active strategy that is based on a proprietary quantitative strategy.",
    )
    other_quant_models: Optional[str] = Field(
        default=None,
        description="For ETFs where 'quant_strategies_type' is 'Other Quant Model',"
        + " this field provides the name of the specific proprietary quant model"
        + " used as the underlying strategy for the ETF.",
    )
    hedge_fund_type: Optional[str] = Field(
        default=None,
        description="For ETFs where 'other_asset_types' is 'Hedge Fund Replication',"
        + " this field provides detail on the type of hedge fund replication strategy.",
    )
    excludes_financials: Optional[bool] = Field(
        default=None,
        description="For equity ETFs, identifies those ETFs"
        + " where the underlying fund holdings will not hold financials stocks,"
        + " based on the funds intended objective.",
    )
    excludes_technology: Optional[bool] = Field(
        default=None,
        description="For equity ETFs, identifies those ETFs"
        + " where the underlying fund holdings will not hold technology stocks,"
        + " based on the funds intended objective.",
    )
    holds_only_nyse_stocks: Optional[bool] = Field(
        default=None,
        description="If true, the ETF is an equity ETF and holds only stocks listed on NYSE.",
    )
    holds_only_nasdaq_stocks: Optional[bool] = Field(
        default=None,
        description="If true, the ETF is an equity ETF and holds only stocks listed on Nasdaq.",
    )
    holds_mlp: Optional[bool] = Field(
        default=None,
        description="If true, the ETF's investment objective explicitly specifies"
        + " that it holds MLPs as an intended part of its investment strategy.",
    )
    holds_preferred_stock: Optional[bool] = Field(
        default=None,
        description="If true, the ETF's investment objective explicitly specifies"
        + " that it holds preferred stock as an intended part of its investment strategy.",
    )
    holds_closed_end_funds: Optional[bool] = Field(
        default=None,
        description="If true, the ETF's investment objective explicitly specifies"
        + " that it holds closed end funds as an intended part of its investment strategy.",
    )
    holds_adr: Optional[bool] = Field(
        default=None,
        description="If true, he ETF's investment objective explicitly specifies that it holds"
        + " American Depositary Receipts (ADRs) as an intended part of its investment strategy.",
    )
    laddered: Optional[bool] = Field(
        default=None,
        description="For bond ETFs, this field identifies those ETFs that"
        + " specifically hold bonds in a laddered structure,"
        + " where the bonds are scheduled to mature in an annual, sequential structure.",
    )
    zero_coupon: Optional[bool] = Field(
        default=None,
        description="For bond ETFs, this field identifies those ETFs that specifically hold zero coupon Treasury Bills.",
    )
    floating_rate: Optional[bool] = Field(
        default=None,
        description="For bond ETFs, this field identifies those ETFs that specifically hold floating rate bonds.",
    )
    build_america_bonds: Optional[bool] = Field(
        default=None,
        description="For municipal bond ETFs, this field identifies those"
        + " ETFs that specifically hold Build America Bonds.",
    )
    dynamic_futures_roll: Optional[bool] = Field(
        default=None,
        description="If the product holds futures contracts, this field identifies those products where the roll strategy"
        + " is dynamic (rather than entirely rules based), so as to minimize roll costs.",
    )
    currency_hedged: Optional[bool] = Field(
        default=None,
        description="This field is populated if the ETF's strategy involves hedging currency exposure.",
    )
    includes_short_exposure: Optional[bool] = Field(
        default=None,
        description="This field is populated if the ETF has short exposure"
        + " in any of its holdings e.g. in a long/short or inverse ETF.",
    )
    ucits: Optional[bool] = Field(
        default=None,
        description="If true, the Exchange Traded Product (ETP) is Undertakings for the Collective Investment"
        + " in Transferable Securities (UCITS) compliant",
    )
    registered_countries: Optional[str] = Field(
        default=None,
        description="The list of countries where the ETF is legally registered for sale."
        + " This may differ from where the ETF is domiciled or traded, particularly in Europe.",
    )
    issuer_country: Optional[str] = Field(
        default=None,
        description="2 letter ISO country code for the country where the issuer is located.",
    )
    domicile: Optional[str] = Field(
        default=None,
        description="2 letter ISO country code for the country where the ETP is domiciled.",
    )
    listing_country: Optional[str] = Field(
        default=None,
        description="2 letter ISO country code for the country of the primary listing.",
        alias="listing_country_code",
    )
    listing_region: Optional[str] = Field(
        default=None,
        description="Geographic region in the country of the primary listing falls.",
    )
    bond_currency_denomination: Optional[str] = Field(
        default=None,
        description="For all bond ETFs, this field provides additional"
        + " detail on the currency denomination of the underlying securities.",
    )
    base_currency: Optional[str] = Field(
        default=None,
        description="Base currency in which NAV is reported.",
    )
    listing_currency: Optional[str] = Field(
        default=None,
        description="Listing currency of the Exchange Traded Product (ETP) in which it is traded."
        + " Reported using the 3-digit ISO currency code.",
    )
    number_of_holdings: Optional[int] = Field(
        default=None,
        description="The number of holdings in the ETF.",
    )
    month_end_assets: Optional[float] = Field(
        default=None,
        description="Net assets in millions of dollars as of the most recent month end.",
    )
    net_expense_ratio: Optional[float] = Field(
        default=None,
        description="Gross expense net of Fee Waivers, as a percentage of net assets"
        + " as published by the ETF issuer.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    etf_portfolio_turnover: Optional[float] = Field(
        default=None,
        description="The percentage of positions turned over in the last 12 months.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class IntrinioEtfInfoFetcher(
    Fetcher[IntrinioEtfInfoQueryParams, List[IntrinioEtfInfoData]]
):
    """Intrinio ETF Info Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioEtfInfoQueryParams:
        """Transform query."""
        return IntrinioEtfInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioEtfInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""

        api_key = credentials.get("intrinio_api_key") if credentials else ""
        base_url = "https://api-v2.intrinio.com/etfs/"
        symbols = query.symbol.split(",")
        symbols = [
            symbol + ":US" if ":" not in symbol else symbol for symbol in symbols
        ]
        urls = [f"{base_url}{symbol}?api_key={api_key}" for symbol in symbols]

        results = []

        async def response_callback(response, _):
            """Response callback."""
            result = await response.json()
            if "error" in result:
                warn(f"Symbol Error: {result['error']} for {response.url.parts[-1]}")
                return
            _ = result.pop("messages", None)
            results.append(result)

        await amake_requests(urls, response_callback, **kwargs)  # type: ignore

        if not results:
            raise EmptyDataError("No data was returned.")

        return sorted(
            results,
            key=(lambda item: (symbols.index(item.get("figi_ticker", len(symbols))))),
        )

    @staticmethod
    def transform_data(
        query: IntrinioEtfInfoQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioEtfInfoData]:
        """Transform data."""
        return [IntrinioEtfInfoData.model_validate(d) for d in data]
