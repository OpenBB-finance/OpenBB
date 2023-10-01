"""GraphQL query definitions."""


class GQL:
    """Class for generating GraphQL queries."""

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
        marketPlace
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

    get_timeseries_query = """query getTimeSeriesData(
      $symbol: String!,
      $freq: String,
      $interval: Int,
      $start: String,
      $end: String,
      $startDateTime: Int,
      $endDateTime: Int
    ) {
      timeseries: getTimeSeriesData(
        symbol: $symbol,
        freq: $freq,
        interval: $interval,
        start: $start,
        end: $end,
        startDateTime: $startDateTime,
        endDateTime: $endDateTime
    ) {
      dateTime
      open
      high
      low
      close
      volume
      __typename
      }
    }"""

    get_timeseries_payload = {
        "operationName": "getTimeSeriesData",
        "variables": {
            "symbol": "BNS",
            "freq": "day",
            "interval": "",
            "start": "2013-09-30",
            "end": "",
            "startDateTime": "",
            "endDateTime": "",
        },
        "query": get_timeseries_query,
    }

    get_company_price_history_query = """query getCompanyPriceHistoryForDownload(
      $symbol: String!,
      $start: String,
      $end: String,
      $adjusted: Boolean,
      $adjustmentType: String,
      $unadjusted: Boolean,
    ) {
      company_price_history: getCompanyPriceHistoryForDownload(
        symbol: $symbol,
        start: $start,
        end: $end,
        adjusted: $adjusted,
        adjustmentType: $adjustmentType,
        unadjusted: $unadjusted,
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
      __typename
      }
    }"""

    get_company_price_history_payload = {
        "operationName": "getCompanyPriceHistoryForDownload",
        "variables": {
            "adjusted": "true",
            "adjustmentType": "SO",
            "end": "2023-09-30",
            "start": "2023-07-03",
            "symbol": "BNS",
            "unadjusted": "false",
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
      __typename
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
        __typename
      }
      events: getUpComingEventsForSymbol(symbol: $symbol, locale: $locale) {
        title
        date
        status
        type
        __typename
        }
      }
    """

    get_company_news_events_payload = {
        "operationName": "getNewsAndEvents",
        "variables": {"symbol": "ART", "page": 1, "limit": 100, "locale": "en"},
        "query": get_company_news_events_query,
    }

    get_company_filings_query = """query getCompanyFilings(
      $symbol: String!
      $fromDate: String
      $toDate: String
      $limit: Int
    ) {
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
        __typename
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
