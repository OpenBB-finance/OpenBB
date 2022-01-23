# IMPORTATION STANDARD
import gzip
import json

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.sector_industry_analysis import financedatabase_model

YF_UTILS_GET_DICT = {
    "GRGCF": {
        "defaultKeyStatistics": {
            "annualHoldingsTurnover": None,
            "enterpriseToRevenue": None,
            "beta3Year": None,
            "profitMargins": 2.8082001,
            "enterpriseToEbitda": None,
            "52WeekChange": 0.2445035,
            "morningStarRiskRating": None,
            "forwardEps": None,
            "revenueQuarterlyGrowth": None,
            "sharesOutstanding": 46895200,
            "fundInceptionDate": None,
            "annualReportExpenseRatio": None,
            "totalAssets": None,
            "bookValue": None,
            "sharesShort": None,
            "sharesPercentSharesOut": None,
            "fundFamily": None,
            "lastFiscalYearEnd": 1609372800,
            "heldPercentInstitutions": 0.72378,
            "netIncomeToCommon": None,
            "trailingEps": None,
            "lastDividendValue": None,
            "SandP52WeekChange": 0.18828869,
            "priceToBook": None,
            "heldPercentInsiders": 0.23013,
            "nextFiscalYearEnd": 1672444800,
            "yield": None,
            "mostRecentQuarter": 1632960000,
            "shortRatio": None,
            "sharesShortPreviousMonthDate": None,
            "floatShares": 37399430,
            "beta": 1.400947,
            "enterpriseValue": 396381024,
            "priceHint": 2,
            "threeYearAverageReturn": None,
            "lastSplitDate": None,
            "lastSplitFactor": None,
            "legalType": None,
            "lastDividendDate": None,
            "morningStarOverallRating": None,
            "earningsQuarterlyGrowth": -0.423,
            "priceToSalesTrailing12Months": None,
            "dateShortInterest": None,
            "pegRatio": None,
            "ytdReturn": None,
            "forwardPE": None,
            "maxAge": 1,
            "lastCapGain": None,
            "shortPercentOfFloat": None,
            "sharesShortPriorMonth": None,
            "impliedSharesOutstanding": None,
            "category": None,
            "fiveYearAverageReturn": None,
        },
        "details": None,
        "summaryProfile": {
            "zip": "0179",
            "sector": "Industrials",
            "fullTimeEmployees": 20314,
            "longBusinessSummary": "Georgia Capital PLC is a private...",
            "city": "Tbilisi",
            "phone": "995 322 000 000",
            "country": "Georgia",
            "companyOfficers": [],
            "website": "https://www.georgiacapital.ge",
            "maxAge": 86400,
            "address1": "3-5 Tatishvili street",
            "fax": "995 322 000 900",
            "industry": "Conglomerates",
        },
        "recommendationTrend": None,
        "financialsTemplate": {"code": "N", "maxAge": 1},
        "earnings": None,
        "price": {
            "quoteSourceName": "Delayed Quote",
            "regularMarketOpen": 9,
            "averageDailyVolume3Month": 42,
            "exchange": "PNK",
            "regularMarketTime": 1641915989,
            "volume24Hr": None,
            "regularMarketDayHigh": 9,
            "shortName": "GEORGIA CAPITAL PLC",
            "averageDailyVolume10Day": 275,
            "longName": "Georgia Capital PLC",
            "regularMarketChange": 0,
            "currencySymbol": "$",
            "regularMarketPreviousClose": 9,
            "preMarketPrice": None,
            "exchangeDataDelayedBy": 0,
            "toCurrency": None,
            "postMarketChange": None,
            "postMarketPrice": None,
            "exchangeName": "Other OTC",
            "preMarketChange": None,
            "circulatingSupply": None,
            "regularMarketDayLow": 9,
            "priceHint": 2,
            "currency": "USD",
            "regularMarketPrice": 9,
            "regularMarketVolume": 2750,
            "lastMarket": None,
            "regularMarketSource": "DELAYED",
            "openInterest": None,
            "marketState": "REGULAR",
            "underlyingSymbol": None,
            "marketCap": 431985600,
            "quoteType": "EQUITY",
            "volumeAllCurrencies": None,
            "strikePrice": None,
            "symbol": "GRGCF",
            "maxAge": 1,
            "fromCurrency": None,
            "regularMarketChangePercent": 0,
        },
        "financialData": {
            "ebitdaMargins": 0,
            "profitMargins": 2.8082001,
            "grossMargins": 0.98942,
            "operatingCashflow": None,
            "revenueGrowth": 1.338,
            "operatingMargins": 0,
            "ebitda": None,
            "targetLowPrice": None,
            "recommendationKey": "none",
            "grossProfits": 339174000,
            "freeCashflow": None,
            "targetMedianPrice": None,
            "currentPrice": 9,
            "earningsGrowth": None,
            "currentRatio": None,
            "returnOnAssets": None,
            "numberOfAnalystOpinions": None,
            "targetMeanPrice": None,
            "debtToEquity": None,
            "returnOnEquity": None,
            "targetHighPrice": None,
            "totalCash": None,
            "totalDebt": None,
            "totalRevenue": None,
            "totalCashPerShare": None,
            "financialCurrency": "GEL",
            "maxAge": 86400,
            "revenuePerShare": None,
            "quickRatio": None,
            "recommendationMean": None,
        },
        "quoteType": {
            "exchange": "PNK",
            "shortName": "GEORGIA CAPITAL PLC",
            "longName": "Georgia Capital PLC",
            "exchangeTimezoneName": "America/New_York",
            "exchangeTimezoneShortName": "EST",
            "isEsgPopulated": False,
            "gmtOffSetMilliseconds": "-18000000",
            "quoteType": "EQUITY",
            "symbol": "GRGCF",
            "messageBoardId": "finmb_329267401",
            "market": "us_market",
        },
        "calendarEvents": {
            "maxAge": 1,
            "earnings": {
                "earningsDate": [],
                "earningsAverage": None,
                "earningsLow": None,
                "earningsHigh": None,
                "revenueAverage": None,
                "revenueLow": None,
                "revenueHigh": None,
            },
            "exDividendDate": None,
            "dividendDate": None,
        },
        "summaryDetail": {
            "previousClose": 9,
            "regularMarketOpen": 9,
            "twoHundredDayAverage": 8.699631,
            "trailingAnnualDividendYield": None,
            "payoutRatio": 0,
            "volume24Hr": None,
            "regularMarketDayHigh": 9,
            "navPrice": None,
            "averageDailyVolume10Day": 275,
            "totalAssets": None,
            "regularMarketPreviousClose": 9,
            "fiftyDayAverage": 8.928,
            "trailingAnnualDividendRate": None,
            "open": 9,
            "toCurrency": None,
            "averageVolume10days": 275,
            "expireDate": None,
            "yield": None,
            "algorithm": None,
            "dividendRate": None,
            "exDividendDate": None,
            "beta": 1.400947,
            "circulatingSupply": None,
            "startDate": None,
            "regularMarketDayLow": 9,
            "priceHint": 2,
            "currency": "USD",
            "regularMarketVolume": 2750,
            "lastMarket": None,
            "maxSupply": None,
            "openInterest": None,
            "marketCap": 431985600,
            "volumeAllCurrencies": None,
            "strikePrice": None,
            "averageVolume": 42,
            "priceToSalesTrailing12Months": None,
            "dayLow": 9,
            "ask": None,
            "ytdReturn": None,
            "askSize": None,
            "volume": 2750,
            "fiftyTwoWeekHigh": 9.42,
            "forwardPE": None,
            "maxAge": 1,
            "fromCurrency": None,
            "fiveYearAvgDividendYield": None,
            "fiftyTwoWeekLow": 7.2318,
            "bid": None,
            "tradeable": False,
            "dividendYield": None,
            "bidSize": None,
            "dayHigh": 9,
        },
        "symbol": "GRGCF",
        "esgScores": None,
        "upgradeDowngradeHistory": None,
        "pageViews": None,
    }
}


def filter_json_data(response):
    """To reduce cassette size."""

    headers = response["headers"]
    if "FILTERED" in headers:
        return response

    if "gzip" in headers.get("Content-Encoding", {}) or "gzip" in headers.get(
        "content-encoding", {}
    ):
        limit = 10
        content_gz = response["body"]["string"]
        content_json = gzip.decompress(content_gz).decode()
        content = json.loads(content_json)

        if isinstance(content, list):
            new_content = content[:limit]
        elif isinstance(content, dict):
            new_content = {k: content[k] for k in list(content)[:limit]}
        else:
            raise AttributeError(f"Content type not supported : {content}")

        new_content_json = json.dumps(new_content)
        new_content_gz = gzip.compress(new_content_json.encode())
        response["body"]["string"] = new_content_gz
        response["headers"]["FILTERED"] = ["TRUE"]

    return response


@pytest.mark.parametrize(
    "industry, sector",
    [
        ("Uranium", ""),
        ("", "Conglomerates"),
        ("", ""),
    ],
)
def test_get_countries(industry, recorder, sector):
    result = financedatabase_model.get_countries(industry=industry, sector=sector)
    recorder.capture(result)


@pytest.mark.parametrize(
    "industry, country",
    [
        ("Uranium", ""),
        ("", "France"),
        ("", ""),
    ],
)
def test_get_sectors(country, industry, recorder):
    result = financedatabase_model.get_sectors(industry=industry, country=country)
    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "country, sector",
    [
        ("France", ""),
        ("", "Conglomerates"),
        ("France", "Energy"),
        ("", ""),
    ],
)
def test_get_industries(country, recorder, sector):
    result = financedatabase_model.get_industries(country=country, sector=sector)
    recorder.capture(result)


@pytest.mark.vcr
def test_get_marketcap(recorder):
    result = financedatabase_model.get_marketcap()
    recorder.capture(result)


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "country, sector, industry",
    [
        ("Georgia", "Industrials", "Conglomerates"),
        ("Georgia", "Industrials", None),
        ("Georgia", None, "Conglomerates"),
        ("Georgia", None, None),
        (None, "Industrials", "Conglomerates"),
        (None, "Industrials", None),
        (None, None, "Conglomerates"),
    ],
)
def test_filter_stocks(country, sector, industry, mocker):
    target = "gamestonk_terminal.stocks.sector_industry_analysis.financedatabase_model.fd.select_equities"
    mock_select_equities = mocker.Mock(return_value={})
    mocker.patch(target=target, new=mock_select_equities)
    financedatabase_model.filter_stocks(
        country=country,
        sector=sector,
        industry=industry,
        marketcap="",
        exclude_exchanges=True,
    )
    mock_select_equities.assert_called_once()


@pytest.mark.vcr(record_mode="none")
def test_filter_stocks_value_error(mocker):
    target = "gamestonk_terminal.stocks.sector_industry_analysis.financedatabase_model.fd.select_equities"
    mocker.patch(target=target, side_effect=ValueError)
    data = financedatabase_model.filter_stocks(
        country="Georgia",
        sector="Industrials",
        industry="Conglomerates",
        marketcap="",
        exclude_exchanges=True,
    )
    assert isinstance(data, list)
    assert not data


@pytest.mark.vcr(record_mode="none")
def test_filter_stocks_no_param():
    data = financedatabase_model.filter_stocks(
        country=None,
        sector=None,
        industry=None,
        marketcap="",
        exclude_exchanges=True,
    )
    assert isinstance(data, list)
    assert not data


@pytest.mark.vcr(record_mode="none")
def test_filter_stocks_marketcap(mocker):
    target = "gamestonk_terminal.stocks.sector_industry_analysis.financedatabase_model.fd.search_products"
    mock_search_products = mocker.Mock(return_value={})
    mocker.patch(target=target, new=mock_search_products)
    financedatabase_model.filter_stocks(
        country=None,
        sector=None,
        industry=None,
        marketcap="Small Cap",
        exclude_exchanges=True,
    )
    mock_search_products.assert_called_once()


@pytest.mark.vcr
def test_get_stocks_data(mocker, recorder):
    target = "gamestonk_terminal.stocks.sector_industry_analysis.financedatabase_model.yf.utils.get_json"
    mocker.patch(target=target, return_value=YF_UTILS_GET_DICT)
    result = financedatabase_model.get_stocks_data(
        country="Georgia",
        sector="Industrials",
        industry="Conglomerates",
        marketcap="",
        exclude_exchanges=True,
    )
    recorder.capture(result)


@pytest.mark.vcr
def test_get_companies_per_sector_in_country(recorder):
    result = financedatabase_model.get_companies_per_sector_in_country(
        country="Georgia",
        mktcap="Small Cap",
        exclude_exchanges=True,
    )
    recorder.capture(result)


@pytest.mark.vcr
def test_get_companies_per_industry_in_country(recorder):
    result = financedatabase_model.get_companies_per_industry_in_country(
        country="Georgia",
        mktcap="Small Cap",
        exclude_exchanges=True,
    )
    recorder.capture(result)


@pytest.mark.vcr
def test_get_companies_per_industry_in_sector(recorder):
    result = financedatabase_model.get_companies_per_industry_in_sector(
        sector="Conglomerates",
        mktcap="Mid",
        exclude_exchanges=True,
    )
    recorder.capture(result)


@pytest.mark.vcr(record_mode="none")
def test_get_companies_per_industry_in_sector_value_error(mocker):
    target = "gamestonk_terminal.stocks.sector_industry_analysis.financedatabase_model.get_industries"
    mocker.patch(target=target, return_value=["MOCK_INDUSTRY"])
    target = "gamestonk_terminal.stocks.sector_industry_analysis.financedatabase_model.fd.select_equities"
    mocker.patch(target=target, side_effect=ValueError)
    result = financedatabase_model.get_companies_per_industry_in_sector(
        sector="Conglomerates",
        mktcap="Mid",
        exclude_exchanges=True,
    )
    assert isinstance(result, dict)
    assert not result


@pytest.mark.vcr
def test_get_companies_per_country_in_sector(recorder):
    result = financedatabase_model.get_companies_per_country_in_sector(
        sector="Conglomerates",
        mktcap="Mid",
        exclude_exchanges=True,
    )
    recorder.capture(result)


def test_get_companies_per_country_in_industry(recorder):
    result = financedatabase_model.get_companies_per_country_in_industry(
        industry="Uranium",
        mktcap="Mid",
        exclude_exchanges=True,
    )
    recorder.capture(result)
