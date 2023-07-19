from openbb_charting.backend.plotly_ta.ta_class import PlotlyTA
from openbb_core.app.model.chart import ChartFormat
from openbb_core.app.router import Router
from openbb_core.app.utils import basemodel_to_df

router = Router(prefix="")

CHART_FORMAT = ChartFormat.plotly

# TODO: This file has placeholders for the commands we may want to implement.
# Once the charts are implemented we can rethink the structure of this file and
# remove the "pylint disable" comments

# pylint: disable=too-many-lines


def crypto_load(**kwargs):
    raise NotImplementedError("Command `crypto/load` does not have a charting function")


def economy_corecpi(**kwargs):
    raise NotImplementedError(
        "Command `economy/corecpi` does not have a charting function"
    )


def economy_cpi(**kwargs):
    raise NotImplementedError("Command `economy/cpi` does not have a charting function")


def economy_cpi_options(**kwargs):
    raise NotImplementedError(
        "Command `economy/cpi/options` does not have a charting function"
    )


def economy_index(**kwargs):
    raise NotImplementedError(
        "Command `economy/index` does not have a charting function"
    )


def economy_available_indices(**kwargs):
    raise NotImplementedError(
        "Command `economy/available/indices` does not have a charting function"
    )


def economy_macro(**kwargs):
    raise NotImplementedError(
        "Command `economy/macro` does not have a charting function"
    )


def economy_macro_countries(**kwargs):
    raise NotImplementedError(
        "Command `economy/macro/countries` does not have a charting function"
    )


def economy_macro_parameters(**kwargs):
    raise NotImplementedError(
        "Command `economy/macro/parameters` does not have a charting function"
    )


def economy_balance(**kwargs):
    raise NotImplementedError(
        "Command `economy/balance` does not have a charting function"
    )


def economy_bigmac(**kwargs):
    raise NotImplementedError(
        "Command `economy/bigmac` does not have a charting function"
    )


def economy_country_codes(**kwargs):
    raise NotImplementedError(
        "Command `economy/country/codes` does not have a charting function"
    )


def economy_currencies(**kwargs):
    raise NotImplementedError(
        "Command `economy/currencies` does not have a charting function"
    )


def economy_debt(**kwargs):
    raise NotImplementedError(
        "Command `economy/debt` does not have a charting function"
    )


def economy_events(**kwargs):
    raise NotImplementedError(
        "Command `economy/events` does not have a charting function"
    )


def economy_fgdp(**kwargs):
    raise NotImplementedError(
        "Command `economy/fgdp` does not have a charting function"
    )


def economy_fred(**kwargs):
    raise NotImplementedError(
        "Command `economy/fred` does not have a charting function"
    )


def economy_fred_search(**kwargs):
    raise NotImplementedError(
        "Command `economy/fred/search` does not have a charting function"
    )


def economy_futures(**kwargs):
    raise NotImplementedError(
        "Command `economy/futures` does not have a charting function"
    )


def economy_gdp(**kwargs):
    raise NotImplementedError("Command `economy/gdp` does not have a charting function")


def economy_glbonds(**kwargs):
    raise NotImplementedError(
        "Command `economy/glbonds` does not have a charting function"
    )


def economy_indices(**kwargs):
    raise NotImplementedError(
        "Command `economy/indices` does not have a charting function"
    )


def economy_overview(**kwargs):
    raise NotImplementedError(
        "Command `economy/overview` does not have a charting function"
    )


def economy_perfmap(**kwargs):
    raise NotImplementedError(
        "Command `economy/perfmap` does not have a charting function"
    )


def economy_performance(**kwargs):
    raise NotImplementedError(
        "Command `economy/performance` does not have a charting function"
    )


def economy_revenue(**kwargs):
    raise NotImplementedError(
        "Command `economy/revenue` does not have a charting function"
    )


def economy_rgdp(**kwargs):
    raise NotImplementedError(
        "Command `economy/rgdp` does not have a charting function"
    )


def economy_rtps(**kwargs):
    raise NotImplementedError(
        "Command `economy/rtps` does not have a charting function"
    )


def economy_search_index(**kwargs):
    raise NotImplementedError(
        "Command `economy/search/index` does not have a charting function"
    )


def economy_spending(**kwargs):
    raise NotImplementedError(
        "Command `economy/spending` does not have a charting function"
    )


def economy_trust(**kwargs):
    raise NotImplementedError(
        "Command `economy/trust` does not have a charting function"
    )


def economy_usbonds(**kwargs):
    raise NotImplementedError(
        "Command `economy/usbonds` does not have a charting function"
    )


def economy_valuation(**kwargs):
    raise NotImplementedError(
        "Command `economy/valuation` does not have a charting function"
    )


def fixedincome_treasury(**kwargs):
    raise NotImplementedError(
        "Command `fixedincome/treasury` does not have a charting function"
    )


def fixedincome_ycrv(**kwargs):
    raise NotImplementedError(
        "Command `fixedincome/ycrv` does not have a charting function"
    )


def forex_load(**kwargs):
    raise NotImplementedError("Command `forex/load` does not have a charting function")


def news_globalnews(**kwargs):
    raise NotImplementedError(
        "Command `news/globalnews` does not have a charting function"
    )


def news_sectornews(**kwargs):
    raise NotImplementedError(
        "Command `news/sectornews` does not have a charting function"
    )


def providers_benzinga_global_news_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/benzinga/global/news/standardized` does not have a charting function"
    )


def providers_benzinga_stock_news_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/benzinga/stock/news/standardized` does not have a charting function"
    )


def providers_fmp_key_executives_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/key/executives/standardized` does not have a charting function"
    )


def providers_fmp_stock_eod_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/stock/eod/standardized` does not have a charting function"
    )


def providers_fmp_global_news_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/global/news/standardized` does not have a charting function"
    )


def providers_fmp_stock_news_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/stock/news/standardized` does not have a charting function"
    )


def providers_fmp_income_statement_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/income/statement/standardized` does not have a charting function"
    )


def providers_fmp_balance_sheet_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/balance/sheet/standardized` does not have a charting function"
    )


def providers_fmp_cash_flow_statement_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/cash/flow/statement/standardized` does not have a charting function"
    )


def providers_fmp_share_statistics_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/share/statistics/standardized` does not have a charting function"
    )


def providers_fmp_major_indices_eod_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/major/indices/eod/standardized` does not have a charting function"
    )


def providers_fmp_revenue_geographic_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/revenue/geographic/standardized` does not have a charting function"
    )


def providers_fmp_revenue_business_line_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/revenue/business/line/standardized` does not have a charting function"
    )


def providers_fmp_institutional_ownership_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/institutional/ownership/standardized` does not have a charting function"
    )


def providers_fmp_company_overview_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/company/overview/standardized` does not have a charting function"
    )


def providers_fmp_stock_insider_trading_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/stock/insider/trading/standardized` does not have a charting function"
    )


def providers_fmp_stock_ownership_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/stock/ownership/standardized` does not have a charting function"
    )


def providers_fmp_e_s_g_score_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/e/s/g/score/standardized` does not have a charting function"
    )


def providers_fmp_e_s_g_sector_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/e/s/g/sector/standardized` does not have a charting function"
    )


def providers_fmp_e_s_g_risk_rating_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/e/s/g/risk/rating/standardized` does not have a charting function"
    )


def providers_fmp_stock_price_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/stock/price/standardized` does not have a charting function"
    )


def providers_fmp_price_target_consensus_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/price/target/consensus/standardized` does not have a charting function"
    )


def providers_fmp_price_target_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/price/target/standardized` does not have a charting function"
    )


def providers_fmp_analyst_estimates_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/analyst/estimates/standardized` does not have a charting function"
    )


def providers_fmp_earnings_calendar_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/earnings/calendar/standardized` does not have a charting function"
    )


def providers_fmp_earnings_call_transcript_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/earnings/call/transcript/standardized` does not have a charting function"
    )


def providers_fmp_historical_stock_splits_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/historical/stock/splits/standardized` does not have a charting function"
    )


def providers_fmp_historical_dividends_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/historical/dividends/standardized` does not have a charting function"
    )


def providers_fmp_key_metrics_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/key/metrics/standardized` does not have a charting function"
    )


def providers_fmp_s_e_c_filings_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/s/e/c/filings/standardized` does not have a charting function"
    )


def providers_fmp_treasury_rates_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/treasury/rates/standardized` does not have a charting function"
    )


def providers_fmp_executive_compensation_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/executive/compensation/standardized` does not have a charting function"
    )


def providers_fmp_crypto_price_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/crypto/price/standardized` does not have a charting function"
    )


def providers_fmp_crypto_eod_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/crypto/eod/standardized` does not have a charting function"
    )


def providers_fmp_major_indices_price_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/major/indices/price/standardized` does not have a charting function"
    )


def providers_fmp_forex_eod_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/forex/eod/standardized` does not have a charting function"
    )


def providers_polygon_stock_eod_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/stock/eod/standardized` does not have a charting function"
    )


def providers_polygon_stock_news_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/stock/news/standardized` does not have a charting function"
    )


def providers_polygon_balance_sheet_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/balance/sheet/standardized` does not have a charting function"
    )


def providers_polygon_income_statement_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/income/statement/standardized` does not have a charting function"
    )


def providers_polygon_cash_flow_statement_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/cash/flow/statement/standardized` does not have a charting function"
    )


def providers_polygon_stock_price_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/stock/price/standardized` does not have a charting function"
    )


def providers_polygon_crypto_price_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/crypto/price/standardized` does not have a charting function"
    )


def providers_polygon_crypto_eod_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/crypto/eod/standardized` does not have a charting function"
    )


def providers_polygon_major_indices_eod_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/major/indices/eod/standardized` does not have a charting function"
    )


def providers_polygon_major_indices_price_standardized(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/major/indices/price/standardized` does not have a charting function"
    )


def providers_benzinga_global_news_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/benzinga/global/news/simple` does not have a charting function"
    )


def providers_benzinga_stock_news_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/benzinga/stock/news/simple` does not have a charting function"
    )


def providers_fmp_key_executives_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/key/executives/simple` does not have a charting function"
    )


def providers_fmp_stock_eod_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/stock/eod/simple` does not have a charting function"
    )


def providers_fmp_global_news_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/global/news/simple` does not have a charting function"
    )


def providers_fmp_stock_news_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/stock/news/simple` does not have a charting function"
    )


def providers_fmp_income_statement_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/income/statement/simple` does not have a charting function"
    )


def providers_fmp_balance_sheet_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/balance/sheet/simple` does not have a charting function"
    )


def providers_fmp_cash_flow_statement_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/cash/flow/statement/simple` does not have a charting function"
    )


def providers_fmp_share_statistics_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/share/statistics/simple` does not have a charting function"
    )


def providers_fmp_major_indices_eod_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/major/indices/eod/simple` does not have a charting function"
    )


def providers_fmp_revenue_geographic_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/revenue/geographic/simple` does not have a charting function"
    )


def providers_fmp_revenue_business_line_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/revenue/business/line/simple` does not have a charting function"
    )


def providers_fmp_institutional_ownership_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/institutional/ownership/simple` does not have a charting function"
    )


def providers_fmp_company_overview_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/company/overview/simple` does not have a charting function"
    )


def providers_fmp_stock_insider_trading_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/stock/insider/trading/simple` does not have a charting function"
    )


def providers_fmp_stock_ownership_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/stock/ownership/simple` does not have a charting function"
    )


def providers_fmp_e_s_g_score_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/e/s/g/score/simple` does not have a charting function"
    )


def providers_fmp_e_s_g_sector_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/e/s/g/sector/simple` does not have a charting function"
    )


def providers_fmp_e_s_g_risk_rating_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/e/s/g/risk/rating/simple` does not have a charting function"
    )


def providers_fmp_stock_price_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/stock/price/simple` does not have a charting function"
    )


def providers_fmp_price_target_consensus_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/price/target/consensus/simple` does not have a charting function"
    )


def providers_fmp_price_target_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/price/target/simple` does not have a charting function"
    )


def providers_fmp_analyst_estimates_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/analyst/estimates/simple` does not have a charting function"
    )


def providers_fmp_earnings_calendar_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/earnings/calendar/simple` does not have a charting function"
    )


def providers_fmp_earnings_call_transcript_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/earnings/call/transcript/simple` does not have a charting function"
    )


def providers_fmp_historical_stock_splits_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/historical/stock/splits/simple` does not have a charting function"
    )


def providers_fmp_historical_dividends_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/historical/dividends/simple` does not have a charting function"
    )


def providers_fmp_key_metrics_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/key/metrics/simple` does not have a charting function"
    )


def providers_fmp_s_e_c_filings_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/s/e/c/filings/simple` does not have a charting function"
    )


def providers_fmp_treasury_rates_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/treasury/rates/simple` does not have a charting function"
    )


def providers_fmp_executive_compensation_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/executive/compensation/simple` does not have a charting function"
    )


def providers_fmp_crypto_price_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/crypto/price/simple` does not have a charting function"
    )


def providers_fmp_crypto_eod_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/crypto/eod/simple` does not have a charting function"
    )


def providers_fmp_major_indices_price_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/major/indices/price/simple` does not have a charting function"
    )


def providers_fmp_forex_eod_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/fmp/forex/eod/simple` does not have a charting function"
    )


def providers_polygon_stock_eod_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/stock/eod/simple` does not have a charting function"
    )


def providers_polygon_stock_news_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/stock/news/simple` does not have a charting function"
    )


def providers_polygon_balance_sheet_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/balance/sheet/simple` does not have a charting function"
    )


def providers_polygon_income_statement_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/income/statement/simple` does not have a charting function"
    )


def providers_polygon_cash_flow_statement_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/cash/flow/statement/simple` does not have a charting function"
    )


def providers_polygon_stock_price_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/stock/price/simple` does not have a charting function"
    )


def providers_polygon_crypto_price_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/crypto/price/simple` does not have a charting function"
    )


def providers_polygon_crypto_eod_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/crypto/eod/simple` does not have a charting function"
    )


def providers_polygon_major_indices_eod_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/major/indices/eod/simple` does not have a charting function"
    )


def providers_polygon_major_indices_price_simple(**kwargs):
    raise NotImplementedError(
        "Command `providers/polygon/major/indices/price/simple` does not have a charting function"
    )


def qa_normality(**kwargs):
    raise NotImplementedError(
        "Command `qa/normality` does not have a charting function"
    )


def qa_capm(**kwargs):
    raise NotImplementedError("Command `qa/capm` does not have a charting function")


def qa_qqplot(**kwargs):
    raise NotImplementedError("Command `qa/qqplot` does not have a charting function")


def qa_om(**kwargs):
    raise NotImplementedError("Command `qa/om` does not have a charting function")


def qa_kurtosis(**kwargs):
    raise NotImplementedError("Command `qa/kurtosis` does not have a charting function")


def qa_pick(**kwargs):
    raise NotImplementedError("Command `qa/pick` does not have a charting function")


def qa_spread(**kwargs):
    raise NotImplementedError("Command `qa/spread` does not have a charting function")


def qa_rolling(**kwargs):
    raise NotImplementedError("Command `qa/rolling` does not have a charting function")


def qa_var(**kwargs):
    raise NotImplementedError("Command `qa/var` does not have a charting function")


def qa_line(**kwargs):
    raise NotImplementedError("Command `qa/line` does not have a charting function")


def qa_hist(**kwargs):
    raise NotImplementedError("Command `qa/hist` does not have a charting function")


def qa_unitroot(**kwargs):
    raise NotImplementedError("Command `qa/unitroot` does not have a charting function")


def qa_beta(**kwargs):
    raise NotImplementedError("Command `qa/beta` does not have a charting function")


def qa_sh(**kwargs):
    raise NotImplementedError("Command `qa/sh` does not have a charting function")


def qa_so(**kwargs):
    raise NotImplementedError("Command `qa/so` does not have a charting function")


def qa_cusum(**kwargs):
    raise NotImplementedError("Command `qa/cusum` does not have a charting function")


def qa_raw(**kwargs):
    raise NotImplementedError("Command `qa/raw` does not have a charting function")


def qa_cdf(**kwargs):
    raise NotImplementedError("Command `qa/cdf` does not have a charting function")


def qa_decompose(**kwargs):
    raise NotImplementedError(
        "Command `qa/decompose` does not have a charting function"
    )


def qa_skew(**kwargs):
    raise NotImplementedError("Command `qa/skew` does not have a charting function")


def qa_quantile(**kwargs):
    raise NotImplementedError("Command `qa/quantile` does not have a charting function")


def qa_bw(**kwargs):
    raise NotImplementedError("Command `qa/bw` does not have a charting function")


def qa_es(**kwargs):
    raise NotImplementedError("Command `qa/es` does not have a charting function")


def qa_acf(**kwargs):
    raise NotImplementedError("Command `qa/acf` does not have a charting function")


def qa_summary(**kwargs):
    raise NotImplementedError("Command `qa/summary` does not have a charting function")


def stocks_fa_balance(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/balance` does not have a charting function"
    )


def stocks_fa_cash(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/cash` does not have a charting function"
    )


def stocks_fa_comp(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/comp` does not have a charting function"
    )


def stocks_fa_earning(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/earning` does not have a charting function"
    )


def stocks_fa_emp(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/emp` does not have a charting function"
    )


def stocks_fa_est(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/est` does not have a charting function"
    )


def stocks_fa_income(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/income` does not have a charting function"
    )


def stocks_fa_ins(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/ins` does not have a charting function"
    )


def stocks_fa_metrics(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/metrics` does not have a charting function"
    )


def stocks_fa_mgmt(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/mgmt` does not have a charting function"
    )


def stocks_fa_overview(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/overview` does not have a charting function"
    )


def stocks_fa_own(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/own` does not have a charting function"
    )


def stocks_fa_pta(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/pta` does not have a charting function"
    )


def stocks_fa_pt(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/pt` does not have a charting function"
    )


def stocks_fa_revgeo(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/revgeo` does not have a charting function"
    )


def stocks_fa_revseg(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/revseg` does not have a charting function"
    )


def stocks_fa_shrs(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/shrs` does not have a charting function"
    )


def stocks_fa_shares(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/shares` does not have a charting function"
    )


def stocks_fa_transcript(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/transcript` does not have a charting function"
    )


def stocks_fa_split(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/split` does not have a charting function"
    )


def stocks_fa_cal(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/cal` does not have a charting function"
    )


def stocks_fa_customer(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/customer` does not have a charting function"
    )


def stocks_fa_divs(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/divs` does not have a charting function"
    )


def stocks_fa_dcfc(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/dcfc` does not have a charting function"
    )


def stocks_fa_dupont(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/dupont` does not have a charting function"
    )


def stocks_fa_enterprise(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/enterprise` does not have a charting function"
    )


def stocks_fa_epsfc(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/epsfc` does not have a charting function"
    )


def stocks_fa_analysis(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/analysis` does not have a charting function"
    )


def stocks_fa_fama_coe(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/fama/coe` does not have a charting function"
    )


def stocks_fa_fama_raw(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/fama/raw` does not have a charting function"
    )


def stocks_fa_fraud(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/fraud` does not have a charting function"
    )


def stocks_fa_growth(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/growth` does not have a charting function"
    )


def stocks_fa_historical_5(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/historical/5` does not have a charting function"
    )


def stocks_fa_key(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/key` does not have a charting function"
    )


def stocks_fa_mktcap(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/mktcap` does not have a charting function"
    )


def stocks_fa_news(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/news` does not have a charting function"
    )


def stocks_fa_rating(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/rating` does not have a charting function"
    )


def stocks_fa_ratios(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/ratios` does not have a charting function"
    )


def stocks_fa_revfc(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/revfc` does not have a charting function"
    )


def stocks_fa_rot(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/rot` does not have a charting function"
    )


def stocks_fa_score(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/score` does not have a charting function"
    )


def stocks_fa_sec(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/sec` does not have a charting function"
    )


def stocks_fa_supplier(**kwargs):
    raise NotImplementedError(
        "Command `stocks/fa/supplier` does not have a charting function"
    )


def stocks_ca_get(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ca/get` does not have a charting function"
    )


def stocks_ca_balance(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ca/balance` does not have a charting function"
    )


def stocks_ca_cashflow(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ca/cashflow` does not have a charting function"
    )


def stocks_ca_hcorr(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ca/hcorr` does not have a charting function"
    )


def stocks_ca_hist(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ca/hist` does not have a charting function"
    )


def stocks_ca_income(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ca/income` does not have a charting function"
    )


def stocks_ca_scorr(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ca/scorr` does not have a charting function"
    )


def stocks_ca_screener(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ca/screener` does not have a charting function"
    )


def stocks_ca_sentiment(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ca/sentiment` does not have a charting function"
    )


def stocks_ca_similar(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ca/similar` does not have a charting function"
    )


def stocks_ca_volume(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ca/volume` does not have a charting function"
    )


def stocks_dd_sec(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dd/sec` does not have a charting function"
    )


def stocks_dps_psi(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dps/psi` does not have a charting function"
    )


def stocks_dps_ctb(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dps/ctb` does not have a charting function"
    )


def stocks_dps_dpotc(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dps/dpotc` does not have a charting function"
    )


def stocks_dps_ftd(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dps/ftd` does not have a charting function"
    )


def stocks_dps_hsi(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dps/hsi` does not have a charting function"
    )


def stocks_dps_pos(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dps/pos` does not have a charting function"
    )


def stocks_dps_prom(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dps/prom` does not have a charting function"
    )


def stocks_dps_psi_q(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dps/psi/q` does not have a charting function"
    )


def stocks_dps_psi_sg(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dps/psi/sg` does not have a charting function"
    )


def stocks_dps_shorted(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dps/shorted` does not have a charting function"
    )


def stocks_dps_sidtc(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dps/sidtc` does not have a charting function"
    )


def stocks_dps_spos(**kwargs):
    raise NotImplementedError(
        "Command `stocks/dps/spos` does not have a charting function"
    )


def stocks_disc_active(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/active` does not have a charting function"
    )


def stocks_disc_arkord(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/arkord` does not have a charting function"
    )


def stocks_disc_asc(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/asc` does not have a charting function"
    )


def stocks_disc_dividends(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/dividends` does not have a charting function"
    )


def stocks_disc_filings(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/filings` does not have a charting function"
    )


def stocks_disc_fipo(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/fipo` does not have a charting function"
    )


def stocks_disc_gainers(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/gainers` does not have a charting function"
    )


def stocks_disc_gtech(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/gtech` does not have a charting function"
    )


def stocks_disc_hotpenny(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/hotpenny` does not have a charting function"
    )


def stocks_disc_ipo(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/ipo` does not have a charting function"
    )


def stocks_disc_losers(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/losers` does not have a charting function"
    )


def stocks_disc_lowfloat(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/lowfloat` does not have a charting function"
    )


def stocks_disc_pipo(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/pipo` does not have a charting function"
    )


def stocks_disc_rtat(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/rtat` does not have a charting function"
    )


def stocks_disc_trending(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/trending` does not have a charting function"
    )


def stocks_disc_ugs(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/ugs` does not have a charting function"
    )


def stocks_disc_ulc(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/ulc` does not have a charting function"
    )


def stocks_disc_upcoming(**kwargs):
    raise NotImplementedError(
        "Command `stocks/disc/upcoming` does not have a charting function"
    )


def stocks_gov_contracts(**kwargs):
    raise NotImplementedError(
        "Command `stocks/gov/contracts` does not have a charting function"
    )


def stocks_gov_government_trading(**kwargs):
    raise NotImplementedError(
        "Command `stocks/gov/government/trading` does not have a charting function"
    )


def stocks_gov_gtrades(**kwargs):
    raise NotImplementedError(
        "Command `stocks/gov/gtrades` does not have a charting function"
    )


def stocks_gov_histcont(**kwargs):
    raise NotImplementedError(
        "Command `stocks/gov/histcont` does not have a charting function"
    )


def stocks_gov_lastcontracts(**kwargs):
    raise NotImplementedError(
        "Command `stocks/gov/lastcontracts` does not have a charting function"
    )


def stocks_gov_lasttrades(**kwargs):
    raise NotImplementedError(
        "Command `stocks/gov/lasttrades` does not have a charting function"
    )


def stocks_gov_lobbying(**kwargs):
    raise NotImplementedError(
        "Command `stocks/gov/lobbying` does not have a charting function"
    )


def stocks_gov_qtrcontracts(**kwargs):
    raise NotImplementedError(
        "Command `stocks/gov/qtrcontracts` does not have a charting function"
    )


def stocks_gov_topbuys(**kwargs):
    raise NotImplementedError(
        "Command `stocks/gov/topbuys` does not have a charting function"
    )


def stocks_gov_toplobbying(**kwargs):
    raise NotImplementedError(
        "Command `stocks/gov/toplobbying` does not have a charting function"
    )


def stocks_gov_topsells(**kwargs):
    raise NotImplementedError(
        "Command `stocks/gov/topsells` does not have a charting function"
    )


def stocks_ins_act(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/act` does not have a charting function"
    )


def stocks_ins_blcp(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/blcp` does not have a charting function"
    )


def stocks_ins_blcs(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/blcs` does not have a charting function"
    )


def stocks_ins_blip(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/blip` does not have a charting function"
    )


def stocks_ins_blis(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/blis` does not have a charting function"
    )


def stocks_ins_blop(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/blop` does not have a charting function"
    )


def stocks_ins_blos(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/blos` does not have a charting function"
    )


def stocks_ins_filter(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/filter` does not have a charting function"
    )


def stocks_ins_lcb(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/lcb` does not have a charting function"
    )


def stocks_ins_lins(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/lins` does not have a charting function"
    )


def stocks_ins_lip(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/lip` does not have a charting function"
    )


def stocks_ins_lis(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/lis` does not have a charting function"
    )


def stocks_ins_lit(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/lit` does not have a charting function"
    )


def stocks_ins_lpsb(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/lpsb` does not have a charting function"
    )


def stocks_ins_print_insider_data(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/print/insider/data` does not have a charting function"
    )


def stocks_ins_stats(**kwargs):
    raise NotImplementedError(
        "Command `stocks/ins/stats` does not have a charting function"
    )


def stocks_options_chains(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/chains` does not have a charting function"
    )


def stocks_options_dte(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/dte` does not have a charting function"
    )


def stocks_options_eodchain(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/eodchain` does not have a charting function"
    )


def stocks_options_expirations(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/expirations` does not have a charting function"
    )


def stocks_options_grhist(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/grhist` does not have a charting function"
    )


def stocks_options_hist(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/hist` does not have a charting function"
    )


def stocks_options_info(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/info` does not have a charting function"
    )


def stocks_options_last_price(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/last/price` does not have a charting function"
    )


def stocks_options_oi(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/oi` does not have a charting function"
    )


def stocks_options_pcr(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/pcr` does not have a charting function"
    )


def stocks_options_price(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/price` does not have a charting function"
    )


def stocks_options_unu(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/unu` does not have a charting function"
    )


def stocks_options_voi(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/voi` does not have a charting function"
    )


def stocks_options_vol(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/vol` does not have a charting function"
    )


def stocks_options_vsurf(**kwargs):
    raise NotImplementedError(
        "Command `stocks/options/vsurf` does not have a charting function"
    )


def stocks_load(**kwargs):
    def handle_indicators(ma):
        k = {}
        if ma:
            k["rma"] = dict(length=ma)
        return k

    data = basemodel_to_df(
        kwargs["command_output_item"], index=kwargs.get("index", "date")
    )
    ma = kwargs.get("ma", None)
    prepost = kwargs.get("prepost", False)
    symbol = kwargs.get("symbol", "")

    data.name = f"{symbol} historical data"

    ta = PlotlyTA(charting_settings=kwargs["charting_settings"])
    fig = ta.plot(
        data,
        indicators=dict(**handle_indicators(ma)),
        symbol=f"{symbol} historical data",
        prepost=prepost,
    )

    return fig.show(external=True).to_plotly_json()


def stocks_news(**kwargs):
    raise NotImplementedError("Command `stocks/news` does not have a charting function")


def stocks_tob(**kwargs):
    raise NotImplementedError("Command `stocks/tob` does not have a charting function")


def stocks_quote(**kwargs):
    raise NotImplementedError(
        "Command `stocks/quote` does not have a charting function"
    )


def stocks_search(**kwargs):
    raise NotImplementedError(
        "Command `stocks/search` does not have a charting function"
    )


def _ta_ma(ma_type: str, **kwargs):
    data = basemodel_to_df(kwargs["data"], index=kwargs.get("index", "date"))
    window = kwargs.get("window", 50)
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

    return fig.show(external=True).to_plotly_json()


def ta_atr(**kwargs):
    raise NotImplementedError("Command `ta/atr` does not have a charting function")


def ta_fib(**kwargs):
    raise NotImplementedError("Command `ta/fib` does not have a charting function")


def ta_obv(**kwargs):
    raise NotImplementedError("Command `ta/obv` does not have a charting function")


def ta_fisher(**kwargs):
    raise NotImplementedError("Command `ta/fisher` does not have a charting function")


def ta_adosc(**kwargs):
    raise NotImplementedError("Command `ta/adosc` does not have a charting function")


def ta_tv(**kwargs):
    raise NotImplementedError("Command `ta/tv` does not have a charting function")


def ta_bbands(**kwargs):
    raise NotImplementedError("Command `ta/bbands` does not have a charting function")


def ta_multi(**kwargs):
    raise NotImplementedError("Command `ta/multi` does not have a charting function")


def ta_zlma(**kwargs):
    ma_type = "zlma"
    return _ta_ma(ma_type, **kwargs)


def ta_aroon(**kwargs):
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

    return fig.show(external=True).to_plotly_json()


def ta_sma(**kwargs):
    ma_type = "sma"
    return _ta_ma(ma_type, **kwargs)


def ta_demark(**kwargs):
    raise NotImplementedError("Command `ta/demark` does not have a charting function")


def ta_vwap(**kwargs):
    raise NotImplementedError("Command `ta/vwap` does not have a charting function")


def ta_recom(**kwargs):
    raise NotImplementedError("Command `ta/recom` does not have a charting function")


def ta_macd(**kwargs):
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

    return fig.show(external=True).to_plotly_json()


def ta_hma(**kwargs):
    ma_type = "hma"
    return _ta_ma(ma_type, **kwargs)


def ta_donchian(**kwargs):
    raise NotImplementedError("Command `ta/donchian` does not have a charting function")


def ta_ichimoku(**kwargs):
    raise NotImplementedError("Command `ta/ichimoku` does not have a charting function")


def ta_clenow(**kwargs):
    raise NotImplementedError("Command `ta/clenow` does not have a charting function")


def ta_ad(**kwargs):
    raise NotImplementedError("Command `ta/ad` does not have a charting function")


def ta_adx(**kwargs):
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

    return fig.show(external=True).to_plotly_json()


def ta_wma(**kwargs):
    ma_type = "wma"
    return _ta_ma(ma_type, **kwargs)


def ta_cci(**kwargs):
    raise NotImplementedError("Command `ta/cci` does not have a charting function")


def ta_rsi(**kwargs):
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

    return fig.show(external=True).to_plotly_json()


def ta_summary(**kwargs):
    raise NotImplementedError("Command `ta/summary` does not have a charting function")


def ta_stoch(**kwargs):
    raise NotImplementedError("Command `ta/stoch` does not have a charting function")


def ta_rsp(**kwargs):
    raise NotImplementedError("Command `ta/rsp` does not have a charting function")


def ta_kc(**kwargs):
    raise NotImplementedError("Command `ta/kc` does not have a charting function")


def ta_cg(**kwargs):
    raise NotImplementedError("Command `ta/cg` does not have a charting function")


def ta_cones(**kwargs):
    raise NotImplementedError("Command `ta/cones` does not have a charting function")


def ta_ema(**kwargs):
    ma_type = "ema"
    return _ta_ma(ma_type, **kwargs)
