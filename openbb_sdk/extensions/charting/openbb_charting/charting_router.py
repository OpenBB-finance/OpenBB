from typing import Any, Dict, Tuple

from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_charting.core.openbb_figure_table import OpenBBFigureTable
from openbb_charting.core.plotly_ta.ta_class import PlotlyTA
from openbb_core.app.model.charts.chart import ChartFormat
from openbb_core.app.router import Router
from openbb_core.app.utils import basemodel_to_df

router = Router(prefix="")

CHART_FORMAT = ChartFormat.plotly

# TODO: This file has placeholders for the commands we may want to implement.
# Once the charts are implemented we can rethink the structure of this file and
# remove the "pylint disable" comments

# pylint: disable=too-many-lines


def crypto_load(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `crypto/load` does not have a charting function")


def economy_corecpi(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/corecpi` does not have a charting function"
    )


def economy_cpi(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `economy/cpi` does not have a charting function")


def economy_cpi_options(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/cpi/options` does not have a charting function"
    )


def economy_index(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/index` does not have a charting function"
    )


def economy_available_indices(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/available/indices` does not have a charting function"
    )


def economy_macro(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/macro` does not have a charting function"
    )


def economy_macro_countries(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/macro/countries` does not have a charting function"
    )


def economy_macro_parameters(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/macro/parameters` does not have a charting function"
    )


def economy_balance(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/balance` does not have a charting function"
    )


def economy_bigmac(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/bigmac` does not have a charting function"
    )


def economy_country_codes(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/country/codes` does not have a charting function"
    )


def economy_currencies(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/currencies` does not have a charting function"
    )


def economy_debt(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/debt` does not have a charting function"
    )


def economy_events(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/events` does not have a charting function"
    )


def economy_fgdp(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/fgdp` does not have a charting function"
    )


def economy_fred(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/fred` does not have a charting function"
    )


def economy_fred_search(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/fred/search` does not have a charting function"
    )


def economy_futures(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/futures` does not have a charting function"
    )


def economy_gdp(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `economy/gdp` does not have a charting function")


def economy_glbonds(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/glbonds` does not have a charting function"
    )


def economy_indices(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/indices` does not have a charting function"
    )


def economy_overview(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/overview` does not have a charting function"
    )


def economy_perfmap(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/perfmap` does not have a charting function"
    )


def economy_performance(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/performance` does not have a charting function"
    )


def economy_revenue(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/revenue` does not have a charting function"
    )


def economy_rgdp(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/rgdp` does not have a charting function"
    )


def economy_rtps(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/rtps` does not have a charting function"
    )


def economy_search_index(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/search/index` does not have a charting function"
    )


def economy_spending(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/spending` does not have a charting function"
    )


def economy_trust(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/trust` does not have a charting function"
    )


def economy_usbonds(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/usbonds` does not have a charting function"
    )


def economy_valuation(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/valuation` does not have a charting function"
    )


def fixedincome_treasury(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `fixedincome/treasury` does not have a charting function"
    )


def fixedincome_ycrv(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `fixedincome/ycrv` does not have a charting function"
    )


def forex_load(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `forex/load` does not have a charting function")


def news_globalnews(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `news/globalnews` does not have a charting function"
    )


def news_sectornews(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `news/sectornews` does not have a charting function"
    )


def providers_benzinga_global_news_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/benzinga/global/news/standardized` does not have a charting function"
    )


def providers_benzinga_stock_news_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/benzinga/stock/news/standardized` does not have a charting function"
    )


def providers_fmp_key_executives_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/key/executives/standardized` does not have a charting function"
    )


def providers_fmp_stock_historical_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/stock/historical/standardized` does not have a charting function"
    )


def providers_fmp_global_news_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/global/news/standardized` does not have a charting function"
    )


def providers_fmp_stock_news_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/stock/news/standardized` does not have a charting function"
    )


def providers_fmp_income_statement_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/income/statement/standardized` does not have a charting function"
    )


def providers_fmp_balance_sheet_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/balance/sheet/standardized` does not have a charting function"
    )


def providers_fmp_cash_flow_statement_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/cash/flow/statement/standardized` does not have a charting function"
    )


def providers_fmp_share_statistics_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/share/statistics/standardized` does not have a charting function"
    )


def providers_fmp_major_indices_historical_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/major/indices/historical/standardized` does not have a charting function"
    )


def providers_fmp_revenue_geographic_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/revenue/geographic/standardized` does not have a charting function"
    )


def providers_fmp_revenue_business_line_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/revenue/business/line/standardized` does not have a charting function"
    )


def providers_fmp_institutional_ownership_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/institutional/ownership/standardized` does not have a charting function"
    )


def providers_fmp_company_overview_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/company/overview/standardized` does not have a charting function"
    )


def providers_fmp_stock_insider_trading_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/stock/insider/trading/standardized` does not have a charting function"
    )


def providers_fmp_stock_ownership_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/stock/ownership/standardized` does not have a charting function"
    )


def providers_fmp_e_s_g_score_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/e/s/g/score/standardized` does not have a charting function"
    )


def providers_fmp_e_s_g_sector_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/e/s/g/sector/standardized` does not have a charting function"
    )


def providers_fmp_e_s_g_risk_rating_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/e/s/g/risk/rating/standardized` does not have a charting function"
    )


def providers_fmp_stock_price_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/stock/price/standardized` does not have a charting function"
    )


def providers_fmp_price_target_consensus_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/price/target/consensus/standardized` does not have a charting function"
    )


def providers_fmp_price_target_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/price/target/standardized` does not have a charting function"
    )


def providers_fmp_analyst_estimates_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/analyst/estimates/standardized` does not have a charting function"
    )


def providers_fmp_earnings_calendar_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/earnings/calendar/standardized` does not have a charting function"
    )


def providers_fmp_earnings_call_transcript_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/earnings/call/transcript/standardized` does not have a charting function"
    )


def providers_fmp_historical_stock_splits_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/historical/stock/splits/standardized` does not have a charting function"
    )


def providers_fmp_historical_dividends_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/historical/dividends/standardized` does not have a charting function"
    )


def providers_fmp_key_metrics_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/key/metrics/standardized` does not have a charting function"
    )


def providers_fmp_s_e_c_filings_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/s/e/c/filings/standardized` does not have a charting function"
    )


def providers_fmp_treasury_rates_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/treasury/rates/standardized` does not have a charting function"
    )


def providers_fmp_executive_compensation_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/executive/compensation/standardized` does not have a charting function"
    )


def providers_fmp_crypto_price_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/crypto/price/standardized` does not have a charting function"
    )


def providers_fmp_crypto_historical_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/crypto/historical/standardized` does not have a charting function"
    )


def providers_fmp_major_indices_price_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/major/indices/price/standardized` does not have a charting function"
    )


def providers_fmp_forex_historical_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/forex/historical/standardized` does not have a charting function"
    )


def providers_polygon_stock_historical_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/stock/historical/standardized` does not have a charting function"
    )


def providers_polygon_stock_news_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/stock/news/standardized` does not have a charting function"
    )


def providers_polygon_balance_sheet_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/balance/sheet/standardized` does not have a charting function"
    )


def providers_polygon_income_statement_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/income/statement/standardized` does not have a charting function"
    )


def providers_polygon_cash_flow_statement_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/cash/flow/statement/standardized` does not have a charting function"
    )


def providers_polygon_stock_price_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/stock/price/standardized` does not have a charting function"
    )


def providers_polygon_crypto_price_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/crypto/price/standardized` does not have a charting function"
    )


def providers_polygon_crypto_historical_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/crypto/historical/standardized` does not have a charting function"
    )


def providers_polygon_major_indices_historical_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/major/indices/historical/standardized` does not have a charting function"
    )


def providers_polygon_major_indices_price_standardized(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/major/indices/price/standardized` does not have a charting function"
    )


def providers_benzinga_global_news_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/benzinga/global/news/simple` does not have a charting function"
    )


def providers_benzinga_stock_news_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/benzinga/stock/news/simple` does not have a charting function"
    )


def providers_fmp_key_executives_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/key/executives/simple` does not have a charting function"
    )


def providers_fmp_stock_historical_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/stock/historical/simple` does not have a charting function"
    )


def providers_fmp_global_news_simple(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/global/news/simple` does not have a charting function"
    )


def providers_fmp_stock_news_simple(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/stock/news/simple` does not have a charting function"
    )


def providers_fmp_income_statement_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/income/statement/simple` does not have a charting function"
    )


def providers_fmp_balance_sheet_simple(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/balance/sheet/simple` does not have a charting function"
    )


def providers_fmp_cash_flow_statement_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/cash/flow/statement/simple` does not have a charting function"
    )


def providers_fmp_share_statistics_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/share/statistics/simple` does not have a charting function"
    )


def providers_fmp_major_indices_historical_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/major/indices/historical/simple` does not have a charting function"
    )


def providers_fmp_revenue_geographic_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/revenue/geographic/simple` does not have a charting function"
    )


def providers_fmp_revenue_business_line_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/revenue/business/line/simple` does not have a charting function"
    )


def providers_fmp_institutional_ownership_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/institutional/ownership/simple` does not have a charting function"
    )


def providers_fmp_company_overview_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/company/overview/simple` does not have a charting function"
    )


def providers_fmp_stock_insider_trading_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/stock/insider/trading/simple` does not have a charting function"
    )


def providers_fmp_stock_ownership_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/stock/ownership/simple` does not have a charting function"
    )


def providers_fmp_e_s_g_score_simple(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/e/s/g/score/simple` does not have a charting function"
    )


def providers_fmp_e_s_g_sector_simple(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/e/s/g/sector/simple` does not have a charting function"
    )


def providers_fmp_e_s_g_risk_rating_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/e/s/g/risk/rating/simple` does not have a charting function"
    )


def providers_fmp_stock_price_simple(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/stock/price/simple` does not have a charting function"
    )


def providers_fmp_price_target_consensus_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/price/target/consensus/simple` does not have a charting function"
    )


def providers_fmp_price_target_simple(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/price/target/simple` does not have a charting function"
    )


def providers_fmp_analyst_estimates_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/analyst/estimates/simple` does not have a charting function"
    )


def providers_fmp_earnings_calendar_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/earnings/calendar/simple` does not have a charting function"
    )


def providers_fmp_earnings_call_transcript_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/earnings/call/transcript/simple` does not have a charting function"
    )


def providers_fmp_historical_stock_splits_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/historical/stock/splits/simple` does not have a charting function"
    )


def providers_fmp_historical_dividends_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/historical/dividends/simple` does not have a charting function"
    )


def providers_fmp_key_metrics_simple(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/key/metrics/simple` does not have a charting function"
    )


def providers_fmp_s_e_c_filings_simple(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/s/e/c/filings/simple` does not have a charting function"
    )


def providers_fmp_treasury_rates_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/treasury/rates/simple` does not have a charting function"
    )


def providers_fmp_executive_compensation_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/executive/compensation/simple` does not have a charting function"
    )


def providers_fmp_crypto_price_simple(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/crypto/price/simple` does not have a charting function"
    )


def providers_fmp_crypto_historical_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/crypto/historical/simple` does not have a charting function"
    )


def providers_fmp_major_indices_price_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/major/indices/price/simple` does not have a charting function"
    )


def providers_fmp_forex_historical_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/fmp/forex/historical/simple` does not have a charting function"
    )


def providers_polygon_stock_historical_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/stock/historical/simple` does not have a charting function"
    )


def providers_polygon_stock_news_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/stock/news/simple` does not have a charting function"
    )


def providers_polygon_balance_sheet_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/balance/sheet/simple` does not have a charting function"
    )


def providers_polygon_income_statement_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/income/statement/simple` does not have a charting function"
    )


def providers_polygon_cash_flow_statement_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/cash/flow/statement/simple` does not have a charting function"
    )


def providers_polygon_stock_price_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/stock/price/simple` does not have a charting function"
    )


def providers_polygon_crypto_price_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/crypto/price/simple` does not have a charting function"
    )


def providers_polygon_crypto_historical_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/crypto/historical/simple` does not have a charting function"
    )


def providers_polygon_major_indices_historical_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/major/indices/historical/simple` does not have a charting function"
    )


def providers_polygon_major_indices_price_simple(
    **kwargs,
) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `providers/polygon/major/indices/price/simple` does not have a charting function"
    )


def qa_normality(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `qa/normality` does not have a charting function"
    )


def qa_capm(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/capm` does not have a charting function")


def qa_qqplot(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/qqplot` does not have a charting function")


def qa_om(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/om` does not have a charting function")


def qa_kurtosis(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/kurtosis` does not have a charting function")


def qa_pick(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/pick` does not have a charting function")


def qa_spread(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/spread` does not have a charting function")


def qa_rolling(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/rolling` does not have a charting function")


def qa_var(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/var` does not have a charting function")


def qa_line(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/line` does not have a charting function")


def qa_hist(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/hist` does not have a charting function")


def qa_unitroot(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/unitroot` does not have a charting function")


def qa_beta(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/beta` does not have a charting function")


def qa_sh(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/sh` does not have a charting function")


def qa_so(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/so` does not have a charting function")


def qa_cusum(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/cusum` does not have a charting function")


def qa_raw(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/raw` does not have a charting function")


def qa_cdf(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/cdf` does not have a charting function")


def qa_decompose(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `qa/decompose` does not have a charting function"
    )


def qa_skew(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/skew` does not have a charting function")


def qa_quantile(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/quantile` does not have a charting function")


def qa_bw(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/bw` does not have a charting function")


def qa_es(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/es` does not have a charting function")


def qa_acf(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/acf` does not have a charting function")


def qa_summary(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `qa/summary` does not have a charting function")


def stocks_fa_balance(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/balance` does not have a charting function"
    )


def stocks_fa_cash(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/cash` does not have a charting function"
    )


def stocks_fa_comp(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/comp` does not have a charting function"
    )


def stocks_fa_earning(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/earning` does not have a charting function"
    )


def stocks_fa_emp(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/emp` does not have a charting function"
    )


def stocks_fa_est(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/est` does not have a charting function"
    )


def stocks_fa_income(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/income` does not have a charting function"
    )


def stocks_fa_ins(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/ins` does not have a charting function"
    )


def stocks_fa_metrics(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/metrics` does not have a charting function"
    )


def stocks_fa_mgmt(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/mgmt` does not have a charting function"
    )


def stocks_fa_overview(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/overview` does not have a charting function"
    )


def stocks_fa_own(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/own` does not have a charting function"
    )


def stocks_fa_pta(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/pta` does not have a charting function"
    )


def stocks_fa_pt(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/pt` does not have a charting function"
    )


def stocks_fa_revgeo(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/revgeo` does not have a charting function"
    )


def stocks_fa_revseg(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/revseg` does not have a charting function"
    )


def stocks_fa_shrs(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/shrs` does not have a charting function"
    )


def stocks_fa_shares(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/shares` does not have a charting function"
    )


def stocks_fa_transcript(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/transcript` does not have a charting function"
    )


def stocks_fa_split(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/split` does not have a charting function"
    )


def stocks_fa_cal(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/cal` does not have a charting function"
    )


def stocks_fa_customer(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/customer` does not have a charting function"
    )


def stocks_fa_divs(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/divs` does not have a charting function"
    )


def stocks_fa_dcfc(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/dcfc` does not have a charting function"
    )


def stocks_fa_dupont(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/dupont` does not have a charting function"
    )


def stocks_fa_enterprise(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/enterprise` does not have a charting function"
    )


def stocks_fa_epsfc(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/epsfc` does not have a charting function"
    )


def stocks_fa_analysis(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/analysis` does not have a charting function"
    )


def stocks_fa_fama_coe(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/fama/coe` does not have a charting function"
    )


def stocks_fa_fama_raw(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/fama/raw` does not have a charting function"
    )


def stocks_fa_fraud(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/fraud` does not have a charting function"
    )


def stocks_fa_growth(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/growth` does not have a charting function"
    )


def stocks_fa_historical_5(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/historical/5` does not have a charting function"
    )


def stocks_fa_key(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/key` does not have a charting function"
    )


def stocks_fa_mktcap(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/mktcap` does not have a charting function"
    )


def stocks_fa_news(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/news` does not have a charting function"
    )


def stocks_fa_rating(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/rating` does not have a charting function"
    )


def stocks_fa_ratios(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/ratios` does not have a charting function"
    )


def stocks_fa_revfc(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/revfc` does not have a charting function"
    )


def stocks_fa_rot(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/rot` does not have a charting function"
    )


def stocks_fa_score(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/score` does not have a charting function"
    )


def stocks_fa_sec(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/sec` does not have a charting function"
    )


def stocks_fa_supplier(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/supplier` does not have a charting function"
    )


def stocks_ca_get(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ca/get` does not have a charting function"
    )


def stocks_ca_balance(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ca/balance` does not have a charting function"
    )


def stocks_ca_cashflow(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ca/cashflow` does not have a charting function"
    )


def stocks_ca_hcorr(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ca/hcorr` does not have a charting function"
    )


def stocks_ca_hist(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ca/hist` does not have a charting function"
    )


def stocks_ca_income(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ca/income` does not have a charting function"
    )


def stocks_ca_scorr(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ca/scorr` does not have a charting function"
    )


def stocks_ca_screener(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ca/screener` does not have a charting function"
    )


def stocks_ca_sentiment(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ca/sentiment` does not have a charting function"
    )


def stocks_ca_similar(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ca/similar` does not have a charting function"
    )


def stocks_ca_volume(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ca/volume` does not have a charting function"
    )


def stocks_dd_sec(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dd/sec` does not have a charting function"
    )


def stocks_dps_psi(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dps/psi` does not have a charting function"
    )


def stocks_dps_ctb(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dps/ctb` does not have a charting function"
    )


def stocks_dps_dpotc(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dps/dpotc` does not have a charting function"
    )


def stocks_dps_ftd(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dps/ftd` does not have a charting function"
    )


def stocks_dps_hsi(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dps/hsi` does not have a charting function"
    )


def stocks_dps_pos(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dps/pos` does not have a charting function"
    )


def stocks_dps_prom(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dps/prom` does not have a charting function"
    )


def stocks_dps_psi_q(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dps/psi/q` does not have a charting function"
    )


def stocks_dps_psi_sg(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dps/psi/sg` does not have a charting function"
    )


def stocks_dps_shorted(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dps/shorted` does not have a charting function"
    )


def stocks_dps_sidtc(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dps/sidtc` does not have a charting function"
    )


def stocks_dps_spos(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/dps/spos` does not have a charting function"
    )


def stocks_disc_active(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/active` does not have a charting function"
    )


def stocks_disc_arkord(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/arkord` does not have a charting function"
    )


def stocks_disc_asc(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/asc` does not have a charting function"
    )


def stocks_disc_dividends(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/dividends` does not have a charting function"
    )


def stocks_disc_filings(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/filings` does not have a charting function"
    )


def stocks_disc_fipo(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/fipo` does not have a charting function"
    )


def stocks_disc_gainers(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/gainers` does not have a charting function"
    )


def stocks_disc_gtech(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/gtech` does not have a charting function"
    )


def stocks_disc_hotpenny(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/hotpenny` does not have a charting function"
    )


def stocks_disc_ipo(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/ipo` does not have a charting function"
    )


def stocks_disc_losers(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/losers` does not have a charting function"
    )


def stocks_disc_lowfloat(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/lowfloat` does not have a charting function"
    )


def stocks_disc_pipo(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/pipo` does not have a charting function"
    )


def stocks_disc_rtat(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/rtat` does not have a charting function"
    )


def stocks_disc_trending(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/trending` does not have a charting function"
    )


def stocks_disc_ugs(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/ugs` does not have a charting function"
    )


def stocks_disc_ulc(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/ulc` does not have a charting function"
    )


def stocks_disc_upcoming(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/disc/upcoming` does not have a charting function"
    )


def stocks_gov_contracts(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/gov/contracts` does not have a charting function"
    )


def stocks_gov_government_trading(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/gov/government/trading` does not have a charting function"
    )


def stocks_gov_gtrades(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/gov/gtrades` does not have a charting function"
    )


def stocks_gov_histcont(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/gov/histcont` does not have a charting function"
    )


def stocks_gov_lastcontracts(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/gov/lastcontracts` does not have a charting function"
    )


def stocks_gov_lasttrades(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/gov/lasttrades` does not have a charting function"
    )


def stocks_gov_lobbying(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/gov/lobbying` does not have a charting function"
    )


def stocks_gov_qtrcontracts(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/gov/qtrcontracts` does not have a charting function"
    )


def stocks_gov_topbuys(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/gov/topbuys` does not have a charting function"
    )


def stocks_gov_toplobbying(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/gov/toplobbying` does not have a charting function"
    )


def stocks_gov_topsells(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/gov/topsells` does not have a charting function"
    )


def stocks_ins_act(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/act` does not have a charting function"
    )


def stocks_ins_blcp(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/blcp` does not have a charting function"
    )


def stocks_ins_blcs(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/blcs` does not have a charting function"
    )


def stocks_ins_blip(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/blip` does not have a charting function"
    )


def stocks_ins_blis(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/blis` does not have a charting function"
    )


def stocks_ins_blop(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/blop` does not have a charting function"
    )


def stocks_ins_blos(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/blos` does not have a charting function"
    )


def stocks_ins_filter(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/filter` does not have a charting function"
    )


def stocks_ins_lcb(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/lcb` does not have a charting function"
    )


def stocks_ins_lins(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/lins` does not have a charting function"
    )


def stocks_ins_lip(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/lip` does not have a charting function"
    )


def stocks_ins_lis(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/lis` does not have a charting function"
    )


def stocks_ins_lit(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/lit` does not have a charting function"
    )


def stocks_ins_lpsb(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/lpsb` does not have a charting function"
    )


def stocks_ins_print_insider_data(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/print/insider/data` does not have a charting function"
    )


def stocks_ins_stats(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/stats` does not have a charting function"
    )


def stocks_options_chains(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/chains` does not have a charting function"
    )


def stocks_options_dte(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/dte` does not have a charting function"
    )


def stocks_options_historicalchain(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/historicalchain` does not have a charting function"
    )


def stocks_options_expirations(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/expirations` does not have a charting function"
    )


def stocks_options_grhist(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/grhist` does not have a charting function"
    )


def stocks_options_hist(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/hist` does not have a charting function"
    )


def stocks_options_info(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/info` does not have a charting function"
    )


def stocks_options_last_price(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/last/price` does not have a charting function"
    )


def stocks_options_oi(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/oi` does not have a charting function"
    )


def stocks_options_pcr(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/pcr` does not have a charting function"
    )


def stocks_options_price(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/price` does not have a charting function"
    )


def stocks_options_unu(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/unu` does not have a charting function"
    )


def stocks_options_voi(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/voi` does not have a charting function"
    )


def stocks_options_vol(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/vol` does not have a charting function"
    )


def stocks_options_vsurf(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/options/vsurf` does not have a charting function"
    )


def stocks_load(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    def handle_indicators(ma):
        k = {}
        if ma:
            k["rma"] = dict(length=ma)
        return k

    data = basemodel_to_df(kwargs["obbject_item"], index=kwargs.get("index", "date"))
    standard_params = kwargs["standard_params"].__dict__
    ma = standard_params.get("ma", None)
    prepost = standard_params.get("prepost", False)
    symbol = standard_params.get("symbol", "")

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        indicators=dict(**handle_indicators(ma)),
        symbol=f"{symbol} historical data",
        prepost=prepost,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def stocks_news(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    data = basemodel_to_df(kwargs["obbject_item"], index=kwargs.get("index", "date"))
    standard_params = kwargs["standard_params"].__dict__
    columnwidth = standard_params.get("columnwidth", None)

    tbl_fig = OpenBBFigureTable(tabular_data=data, columnwidth=columnwidth)
    content = tbl_fig.to_table().show(external=True).to_plotly_json()

    return tbl_fig, content


def stocks_tob(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `stocks/tob` does not have a charting function")


def stocks_quote(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/quote` does not have a charting function"
    )


def stocks_search(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/search` does not have a charting function"
    )


def _ta_ma(ma_type: str, **kwargs):
    data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))
    window = kwargs.get("windowstocks_load", 50)
    offset = kwargs.get("offset", 0)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        {f"{ma_type.lower()}": dict(length=window, offset=offset)},
        f"{symbol.upper()} {ma_type.upper()}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def ta_atr(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/atr` does not have a charting function")


def ta_fib(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/fib` does not have a charting function")


def ta_obv(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/obv` does not have a charting function")


def ta_fisher(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/fisher` does not have a charting function")


def ta_adosc(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/adosc` does not have a charting function")


def ta_tv(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/tv` does not have a charting function")


def ta_bbands(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/bbands` does not have a charting function")


def ta_multi(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/multi` does not have a charting function")


def ta_zlma(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    ma_type = "zlma"
    return _ta_ma(ma_type, **kwargs)


def ta_aroon(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))
    length = kwargs.get("length", 25)
    scalar = kwargs.get("scalar", 100)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        dict(aroon=dict(length=length, scalar=scalar)),
        f"Aroon on {symbol}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def ta_sma(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    ma_type = "sma"
    return _ta_ma(ma_type, **kwargs)


def ta_demark(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/demark` does not have a charting function")


def ta_vwap(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/vwap` does not have a charting function")


def ta_recom(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/recom` does not have a charting function")


def ta_macd(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))
    fast = kwargs.get("fast", 12)
    slow = kwargs.get("slow", 26)
    signal = kwargs.get("signal", 9)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        dict(macd=dict(fast=fast, slow=slow, signal=signal)),
        f"{symbol.upper()} MACD",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def ta_hma(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    ma_type = "hma"
    return _ta_ma(ma_type, **kwargs)


def ta_donchian(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/donchian` does not have a charting function")


def ta_ichimoku(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/ichimoku` does not have a charting function")


def ta_clenow(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/clenow` does not have a charting function")


def ta_ad(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/ad` does not have a charting function")


def ta_adx(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))
    length = kwargs.get("length", 14)
    scalar = kwargs.get("scalar", 100.0)
    drift = kwargs.get("drift", 1)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        dict(adx=dict(length=length, scalar=scalar, drift=drift)),
        f"Average Directional Movement Index (ADX) {symbol}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def ta_wma(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    ma_type = "wma"
    return _ta_ma(ma_type, **kwargs)


def ta_cci(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/cci` does not have a charting function")


def ta_rsi(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))
    window = kwargs.get("window", 14)
    scalar = kwargs.get("scalar", 100.0)
    drift = kwargs.get("drift", 1)
    symbol = kwargs.get("symbol", "")

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        dict(rsi=dict(length=window, scalar=scalar, drift=drift)),
        f"{symbol.upper()} RSI {window}",
        False,
        volume=False,
    )
    content = fig.show(external=True).to_plotly_json()

    return fig, content


def ta_summary(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/summary` does not have a charting function")


def ta_stoch(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/stoch` does not have a charting function")


def ta_rsp(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/rsp` does not have a charting function")


def ta_kc(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/kc` does not have a charting function")


def ta_cg(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/cg` does not have a charting function")


def ta_cones(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `ta/cones` does not have a charting function")


def ta_ema(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    ma_type = "ema"
    return _ta_ma(ma_type, **kwargs)


def forex_pairs(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `forex/pairs` does not have a charting function")


def economy_const(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/const` does not have a charting function"
    )


def economy_risk(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `economy/risk` does not have a charting function"
    )


def stocks_fa_comsplit(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/comsplit` does not have a charting function"
    )


def stocks_ins_filt(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ins/filt` does not have a charting function"
    )


def stocks_multiples(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    data = basemodel_to_df(kwargs["obbject_item"], index=kwargs.get("index", "date"))
    standard_params = kwargs["standard_params"].__dict__
    columnwidth = standard_params.get("columnwidth", None)

    tbl_fig = OpenBBFigureTable(tabular_data=data, columnwidth=columnwidth)
    content = tbl_fig.to_table().show(external=True).to_plotly_json()

    return tbl_fig, content


def stocks_fa_balance_growth(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/balance/growth` does not have a charting function"
    )


def stocks_fa_cash_growth(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/cash/growth` does not have a charting function"
    )


def stocks_fa_income_growth(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/income/growth` does not have a charting function"
    )


def stocks_fa_ins_own(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/fa/ins/own` does not have a charting function"
    )


def stocks_ca_peers(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `stocks/ca/peers` does not have a charting function"
    )


def stocks_info(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError("Command `stocks/info` does not have a charting function")


def fixedincome_sofr(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `fixedincome/sofr` does not have a charting function"
    )


def fixedincome_estr(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `fixedincome/estr` does not have a charting function"
    )


def fixedincome_sonia(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `fixedincome/sonia` does not have a charting function"
    )


def fixedincome_ameribor(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `fixedincome/ameribor` does not have a charting function"
    )


def fixedincome_fed(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `fixedincome/fed` does not have a charting function"
    )


def fixedincome_projections(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `fixedincome/projections` does not have a charting function"
    )


def fixedincome_iorb(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `fixedincome/iorb` does not have a charting function"
    )


def futures_load(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `futures/load` does not have a charting function"
    )


def futures_curve(**kwargs) -> Tuple[OpenBBFigure, Dict[str, Any]]:
    raise NotImplementedError(
        "Command `futures/curve` does not have a charting function"
    )
