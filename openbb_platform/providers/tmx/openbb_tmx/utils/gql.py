"""GraphQL query definitions."""

# pylint: disable=line-too-long
# ruff: noqa: E501

stock_info_query = """ query getQuoteBySymbol(
  $symbol: String,
  $locale: String
) {
  getQuoteBySymbol(symbol: $symbol, locale: $locale) {
    symbol
    name
    price
    priceChange
    percentChange
    exchangeName
    exShortName
    exchangeCode
    sector
    industry
    volume
    openPrice
    dayHigh
    dayLow
    MarketCap
    MarketCapAllClasses
    peRatio
    prevClose
    dividendFrequency
    dividendYield
    dividendAmount
    dividendCurrency
    beta
    eps
    exDividendDate
    shortDescription
    longDescription
    website
    email
    phoneNumber
    fullAddress
    employees
    shareOutStanding
    totalDebtToEquity
    totalSharesOutStanding
    sharesESCROW
    vwap
    dividendPayDate
    weeks52high
    weeks52low
    alpha
    averageVolume10D
    averageVolume30D
    averageVolume50D
    priceToBook
    priceToCashFlow
    returnOnEquity
    returnOnAssets
    day21MovingAvg
    day50MovingAvg
    day200MovingAvg
    dividend3Years
    dividend5Years
    datatype
    issueType
    qmdescription
  }
}
"""

stock_info_payload = {
    "operationName": "getQuoteBySymbol",
    "variables": {"locale": "en"},
    "query": stock_info_query,
}

get_timeseries_query = """query getTimeSeriesData($symbol: String!, $freq: String, $interval: Int, $start: String, $end: String, $startDateTime: Int, $endDateTime: Int) {
 getTimeSeriesData(
 symbol: $symbol
 freq: $freq
 interval: $interval
 start: $start
 end: $end
 startDateTime: $startDateTime
 endDateTime: $endDateTime
 ) {
 dateTime
 open
 high
 low
 close
 volume
}
}"""

get_timeseries_payload = {
    "operationName": "getTimeSeriesData",
    "variables": {
        "symbol": "BNS",
        "freq": "day",
        "interval": "",
        "start": "2013-09-30",
        "end": "2013-10-31",
        "startDateTime": "",
        "endDateTime": "",
    },
    "query": get_timeseries_query,
}

get_company_price_history_query = """query getCompanyPriceHistory($symbol: String!, $start: String, $end: String, $adjusted: Boolean, $adjustmentType: String, $unadjusted: Boolean, $limit: Int) {
 getCompanyPriceHistory(
 symbol: $symbol
 start: $start
 end: $end
 adjusted: $adjusted
 adjustmentType: $adjustmentType
 unadjusted: $unadjusted
 limit: $limit
 ) {
 datetime
 openPrice
 closePrice
 high
 low
 volume
 tradeValue
 numberOfTrade
 change
 changePercent
 vwap
}
}"""

get_company_price_history_payload = {
    "operationName": "getCompanyPriceHistory",
    "variables": {
        "adjusted": True,
        "adjustmentType": "SO",
        "end": "2023-10-28",
        "start": "2023-10-01",
        "symbol": "BNS",
        "unadjusted": False,
    },
    "query": get_company_price_history_query,
}

get_company_most_recent_trades_query = """query getCompanyMostRecentTrades(
  $symbol: String!
  $limit: Int
) {
trades: getCompanyMostRecentTrades(
  symbol: $symbol,
  limit: $limit
) {
  price
  volume
  datetime
  sellerId
  sellerName
  buyerId
  buyerName
  exchangeCode
  }
}
"""

get_company_most_recent_trades_payload = {
    "operationName": "getCompanyMostRecentTrades",
    "variables": {
        "symbol": "BNS",
        "limit": 51,
    },
    "query": get_company_most_recent_trades_query,
}

get_company_news_events_query = """query getNewsAndEvents(
  $symbol: String!,
  $page: Int!,
  $limit: Int!,
  $locale: String!
) {
  news: getNewsForSymbol(
    symbol: $symbol,
    page: $page,
    limit: $limit,
    locale: $locale
  ) {
    headline
    datetime
    source
    newsid
    summary
  }
  events: getUpComingEventsForSymbol(symbol: $symbol, locale: $locale) {
    title
    date
    status
    type
    }
  }
"""

get_company_news_events_payload = {
    "operationName": "getNewsAndEvents",
    "variables": {"symbol": "ART", "page": 1, "limit": 100, "locale": "en"},
    "query": get_company_news_events_query,
}

get_company_filings_query = """query getCompanyFilings($symbol: String!, $fromDate: String, $toDate: String, $limit: Int) {
  filings: getCompanyFilings(
  symbol: $symbol
  fromDate: $fromDate
  toDate: $toDate
  limit: $limit
  ) {
size
filingDate
description
name
urlToPdf
}
}"""

get_company_filings_payload = {
    "operationName": "getCompanyFilings",
    "variables": {
        "symbol": "AC",
        "fromDate": "2020-09-01",
        "toDate": "2023-09-20",
        "limit": 100,
    },
    "query": get_company_filings_query,
}

historical_dividends_query = """query getDividendsForSymbol(
  $symbol: String!
  $page: Int,
  $batch: Int
) {
  dividends: getDividendsForSymbol(
    symbol: $symbol
    page: $page
    batch: $batch
  ) {
    pageNumber
    hasNextPage
    dividends
      {
        exDate
        amount
        currency
        payableDate
        declarationDate
        recordDate
    }
  }
}"""

historical_dividends_payload = {
    "operationName": "getDividendsForSymbol",
    "variables": {
        "batch": 10,
        "page": 1,
        "symbol": "BNS",
    },
    "query": historical_dividends_query,
}

get_company_analysts_query = """query getCompanyAnalysts(
  $symbol: String!
  $dataType: String,
) {
  analysts: getCompanyAnalysts(
    datatype: $dataType,
    symbol: $symbol
  ) {
    totalAnalysts
    priceTarget
      {
        highPriceTarget
        lowPriceTarget
        priceTarget
        priceTargetUpside
    }
    consensusAnalysts
      {
      consensus
      buy
      sell
      hold
    }
  }
}"""

get_company_analysts_payload = {
    "operationName": "getCompanyAnalysts",
    "variables": {
        "symbol": "BNS",
        "datatype": "equity",
    },
    "query": get_company_analysts_query,
}

get_earnings_date_query = """query getEnhancedEarningsForDate(
  $date: String!
  ) {
  getEnhancedEarningsForDate(
    date: $date
) {
      symbol
      companyName
      announceTime
      estimatedEps
      actualEps
      epsSurprisePercent
      epsSurpriseDollar
  }
}"""

get_earnings_date_payload = {
    "operationName": "getEnhancedEarningsForDate",
    "variables": {
        "date": "2023-10-04",
    },
    "query": get_earnings_date_query,
}

get_index_overview_query = """query getIndexBySymbol(
  $symbol: String!,
  $locale: String
  ) {
  getIndexBySymbol(
    symbol: $symbol,
    locale: $locale
) {
      name
      intro
      overview
  }
}"""

get_index_overview_payload = {
    "operationName": "getIndexBySymbol",
    "variables": {
        "symbol": "^TSX",
    },
    "query": get_index_overview_query,
}

get_index_constituents_query = """query getIndexConstituents(
  $symbol: String!
) {
    constituents: getIndexConstituents(
      symbol: $symbol
  ) {
      symbol
      quotedMarketValue
      longName
      shortName
      weight
      exShortName
      exchange
      exLongName
  }
    keyData: getIndexKeyData(
      symbol: $symbol
  ) {
      adjMarketCap
      avgConstituentMarketCap
      numConstituents
      top10HoldingsAdjMarketCap
      ytdPriceReturn
      prevDayPriceReturn
      prevMonthPriceReturn
      prevQuarterPriceReturn
      percentWeightLargestConstituent
      peRatio
      pbRatio
      priceToSales
      divYield
      pcfRatio
    }
  }"""

get_index_constituents_payload = {
    "operationName": "getIndexConstituents",
    "variables": {
        "symbol": "^TSX",
    },
    "query": get_index_constituents_query,
}

get_stock_list_query = """query getStockListSymbolsWithQuote(
  $stockListId: String!
  $locale: String,
) {
  stockList: getStockListSymbolsWithQuote(
    stockListId: $stockListId,
    locale: $locale
  ) {
    stockListId
    name
    description
    longDescription
    metricTitle
    listItems
      {
        symbol
        longName
        rank
        metric
        price
        priceChange
        percentChange
        volume
    }
    totalPriceChange
    totalPercentChange
    createdAt
    updatedAt
  }
}"""

get_stock_list_payload = {
    "operationName": "getStockListSymbolsWithQuote",
    "variables": {"locale": "en", "stockListId": "TOP_VOLUME"},
    "query": get_stock_list_query,
}

get_company_insiders_query = """query getCompanyInsidersActivities(
    $symbol: String
) {
    getCompanyInsidersActivities(
      symbol: $symbol
  ) {
    insiderActivities {
      periodkey
      buy {
        name
        trades
        shares
        sharesHeld
        tradeValue
    }
      sell {
        name
        trades
        shares
        sharesHeld
        tradeValue
    }
  }
    activitySummary {
      periodkey
      buyShares
      soldShares
      netActivity
      totalShares
    }
  }
}"""

get_company_insiders_payload = {
    "operationName": "getCompanyInsidersActivities",
    "variables": {
        "symbol": "CNQ",
    },
    "query": get_company_insiders_query,
}


get_quote_for_symbols_query = """query getQuoteForSymbols($symbols: [String]) {
 getQuoteForSymbols(symbols: $symbols) {
 symbol
 longname
 price
 prevClose
 priceChange
 percentChange
 weeks52high
 weeks52low
 }
}"""

get_quote_for_symbols_payload = {
    "operationName": "getQuoteForSymbols",
    "variables": {
        "symbols": [
            "SRE:US",
            "BWVTF:US",
            "C.P.K:US",
            "BAC.PY:US",
            "BALTF:US",
            "BACRP:US",
        ],
    },
    "query": get_quote_for_symbols_query,
}

get_index_price_history_query = """query getIndexPriceHistory($symbol: String!, $start: String, $end: String, $adjusted: Boolean, $adjustmentType: String, $unadjusted: Boolean, $limit: Int) {\n  getIndexPriceHistory(\n    symbol: $symbol\n    start: $start\n    end: $end\n    adjusted: $adjusted\n    adjustmentType: $adjustmentType\n    unadjusted: $unadjusted\n    limit: $limit\n  ) {\n    datetime\n    openPrice\n    closePrice\n    high\n    low\n    volume\n    change\n    changePercent\n    triv\n      }\n}"}"""

get_index_price_history_payload = {
    "operationName": "getIndexPriceHistory",
    "variables": {
        "symbol": "^TSX",
        "start": "2023-12-01",
        "end": "2023-12-31",
        "adjusted": True,
        "adjustmentType": "SO",
        "unadjusted": False,
    },
    "query": get_index_price_history_query,
}
