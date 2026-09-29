"""Shared fixtures for the offline TMX suite."""

import pytest


@pytest.fixture(autouse=True, scope="session")
def _isolated_result_cache(tmp_path_factory):
    """Keep the suite's stubbed results out of the real cache."""
    import os

    from openbb_tmx.utils.memo import CACHE_DIR_ENV

    directory = tmp_path_factory.mktemp("tmx_results")
    previous = os.environ.get(CACHE_DIR_ENV)
    os.environ[CACHE_DIR_ENV] = str(directory)

    yield

    if previous is None:
        os.environ.pop(CACHE_DIR_ENV, None)
    else:
        os.environ[CACHE_DIR_ENV] = previous


SAMPLES: dict = {
    "getQuoteBySymbol": {
        "getQuoteBySymbol": {
            "symbol": "AC",
            "name": "Air Canada",
            "price": 23.27,
            "priceChange": 0.62,
            "percentChange": 2.74,
            "exchangeName": "Toronto Stock Exchange",
            "exShortName": "TSX",
            "exchangeCode": "XTSE",
            "sector": "Industrials",
            "industry": "Airlines",
            "volume": 1958163,
            "openPrice": 22.78,
            "dayHigh": 23.43,
            "dayLow": 22.6,
            "MarketCap": 8000000000,
            "MarketCapAllClasses": 8000000000,
            "peRatio": 6.1,
            "prevClose": 22.65,
            "beta": 1.9,
            "eps": 3.8,
            "longDescription": "Air Canada is an airline.",
            "website": "https://aircanada.com",
            "employees": 38000,
            "totalSharesOutStanding": 350000000,
            "vwap": 23.1,
            "weeks52high": 25.0,
            "weeks52low": 14.0,
            "issueType": "Equity",
            "currency": "CAD",
            "close": 23.27,
            "qmdescription": "Air Canada",
        }
    },
    "getQuoteForSymbols": {
        "getQuoteForSymbols": [
            {
                "symbol": "^TSX",
                "longname": "S&P/TSX",
                "price": 35369.1,
                "percentChange": 0.4,
                "priceChange": 140.0,
                "volume": 1,
            },
        ]
    },
    "getTimeSeriesData": {
        "getTimeSeriesData": [
            {
                "dateTime": "2026-07-23T16:00:00-04:00",
                "open": 22.9,
                "high": 23.4,
                "low": 22.8,
                "close": 23.2,
                "volume": 100,
            },
            {
                "dateTime": "2026-07-24T16:00:00-04:00",
                "open": 23.0,
                "high": 23.5,
                "low": 22.9,
                "close": 23.27,
                "volume": 120,
            },
        ]
    },
    "getCompanyPriceHistory": {
        "getCompanyPriceHistory": [
            {
                "datetime": "2026-07-24",
                "openPrice": 23.0,
                "closePrice": 23.27,
                "high": 23.5,
                "low": 22.9,
                "volume": 120,
                "tradeValue": 2700.0,
                "numberOfTrade": 10,
                "change": 0.62,
                "changePercent": 2.74,
                "vwap": 23.1,
            },
        ]
    },
    "getCompanyMostRecentTrades": {
        "getCompanyMostRecentTrades": [
            {
                "price": 23.27,
                "volume": 95,
                "datetime": "2026-07-24T16:00:00-04:00",
                "sellerId": "79",
                "sellerName": "CIBC",
                "buyerId": "002",
                "buyerName": "RBC",
                "exchangeCode": "TSX",
            },
        ]
    },
    "GetCompanyShortInterest": {
        "getCompanyShortInterest": {
            "TICKER": "AC",
            "BUSINESS_DATE": "2026-07-24",
            "SHORT_INTEREST": 6443193,
            "SHORTINTERESTPCT": 0.0231,
            "DAYSTOCOVER10DAY": None,
            "DAYSTOCOVER30DAY": 2.44,
            "DAYSTOCOVER90DAY": None,
        }
    },
    "getSplitsForSymbol": {
        "getSplitsForSymbol": [{"splitDate": "2004-04-02", "ratio": 0.5}]
    },
    "getDividendsForSymbol": {
        "dividendHistory": {
            "pageNumber": 1,
            "hasNextPage": False,
            "dividends": [
                {
                    "exDate": "2026-04-01",
                    "amount": 1.06,
                    "currency": "CAD",
                    "payableDate": "2026-04-28",
                    "declarationDate": "2026-02-25",
                    "recordDate": "2026-04-02",
                }
            ],
        }
    },
    "getCompanyFilings": {
        "filings": [
            {
                "size": "1.2 MB",
                "filingDate": "2026-06-01",
                "description": "Annual",
                "name": "AIF",
                "urlToPdf": "https://example.com/a.pdf",
            }
        ]
    },
    "getNewsAndEvents": {
        "news": [
            {
                "headline": "Air Canada reports",
                "datetime": "2026-07-24T10:00:00-04:00",
                "source": "CNW",
                "newsid": "123",
                "summary": "Air Canada reports",
            }
        ],
        "events": [
            {
                "title": "Q2 Earnings",
                "date": "2026-08-01",
                "status": "Confirmed",
                "type": "Earnings",
            }
        ],
    },
    "getCompanyAnalysts": {
        "getCompanyAnalysts": {
            "totalAnalysts": 12,
            "priceTarget": {
                "lowPriceTarget": 20.0,
                "highPriceTarget": 32.0,
                "priceTarget": 27.0,
                "priceTargetUpside": 0.16,
            },
            "consensusAnalysts": {"consensus": "Buy", "buy": 8, "sell": 1, "hold": 3},
        }
    },
    "getEnhancedEarningsForDate": {
        "getEnhancedEarningsForDate": [
            {
                "symbol": "AC",
                "companyName": "Air Canada",
                "announceTime": "After Close",
                "estimatedEps": 0.5,
                "actualEps": 0.6,
                "epsSurprisePercent": 20.0,
                "epsSurpriseDollar": 0.1,
            }
        ]
    },
    "getCompanyInsidersActivities": {
        "getCompanyInsidersActivities": {
            "insiderActivities": [
                {
                    "periodkey": "3",
                    "buy": [
                        {
                            "name": "Doe, Jane",
                            "trades": 1,
                            "shares": 100,
                            "sharesHeld": 500,
                            "tradeValue": 2300.0,
                        }
                    ],
                    "sell": [],
                }
            ],
            "activitySummary": [
                {
                    "periodkey": "3",
                    "buyShares": 100,
                    "soldShares": 0,
                    "netActivity": 100,
                    "totalShares": 100,
                    "buyTrades": 1,
                    "sellTrades": 0,
                    "totalTrades": 1,
                }
            ],
        }
    },
    "getStockListSymbolsWithQuote": {
        "stockList": {
            "stockListId": "TOP_VOLUME",
            "name": "Top Volume",
            "description": "d",
            "longDescription": "ld",
            "metricTitle": "Volume",
            "totalPriceChange": 1.0,
            "totalPercentChange": 0.5,
            "createdAt": "2026-01-01",
            "updatedAt": "2026-07-24",
            "listItems": [
                {
                    "symbol": "AC",
                    "longName": "Air Canada",
                    "rank": 1,
                    "metric": 100,
                    "price": 23.27,
                    "priceChange": 0.62,
                    "percentChange": 2.74,
                    "volume": 1958163,
                }
            ],
        }
    },
    "getIndexConstituents": {
        "constituents": [
            {
                "symbol": "RY",
                "longName": "Royal Bank of Canada",
                "shortName": "Royal Bank Of Ca",
                "exchange": "TSX",
                "exLongName": "Toronto Stock Exchange",
                "quotedMarketValue": 412336362030,
                "weight": 8.168,
            }
        ],
        "keyData": {"numConstituents": 219},
    },
    "getIndexKeyData": {
        "getIndexKeyData": {
            "peRatio": 21.26,
            "pbRatio": 2.71,
            "priceToSales": 2.77,
            "pcfRatio": 36.44,
            "divYield": 2.13,
            "numConstituents": 219,
        }
    },
    "getMarketMovers": {
        "getMarketMovers": [
            {
                "symbol": "AC",
                "name": "Air Canada",
                "exchangeName": "TSX",
                "exchangeCode": "XTSE",
                "price": 23.27,
                "priceChange": 0.62,
                "percentChange": 2.74,
                "volume": 1958163,
                "tradeVolume": 9452,
                "open": 22.78,
                "high": 23.43,
                "low": 22.6,
                "weeks52low": 14.0,
                "weeks52high": 25.0,
            }
        ]
    },
}


@pytest.fixture
def gql(monkeypatch):
    """Answer every GraphQL operation from the sample payloads."""
    calls: list = []

    async def fake(
        operation, query, variables=None, symbol=None, use_cache=True, **kwargs
    ):
        calls.append((operation, variables))
        return SAMPLES.get(operation, {})

    monkeypatch.setattr("openbb_tmx.utils.cache.amake_gql_request", fake)

    return calls


@pytest.fixture
def http(monkeypatch):
    """Answer every cached HTTP request from a routing table."""
    routes: dict = {}

    async def fake(url, use_cache=True, accept_type="json", **kwargs):
        for fragment, payload in routes.items():
            if fragment in url:
                return payload

        return None

    monkeypatch.setattr("openbb_tmx.utils.cache.amake_request", fake)

    return routes


UNDERLYING_PRICE = 23.0

CHAIN_STRIKES = (19.0, 21.0, 23.0, 25.0, 27.0)

CHAIN_TENORS = (7, 35, 63)


def _contract_quote(expiry, strike, side, index, priced=True):
    """Build one vendor quote for the synthetic chain."""
    distance = abs(strike - UNDERLYING_PRICE) / UNDERLYING_PRICE
    premium = round(max(0.05, (UNDERLYING_PRICE * 0.04) - (distance * 6.9)), 2)
    contract = f"{expiry.replace('-', '')}{side[0]}{int(strike * 1000):08d}"

    return {
        "contract": {
            "expirydate": expiry,
            "callput": side,
            "strike": strike,
            "type": "STANDARD",
            "openinterest": 100 + index * 7,
            "contracthigh": premium + 0.5,
            "contractlow": max(0.01, premium - 0.5),
        },
        "pricedata": {
            "last": premium,
            "bid": round(premium - 0.02, 2),
            "ask": round(premium + 0.02, 2),
            "bidsize": 10,
            "asksize": 12,
            "contractvolume": 5 + index,
            "prevclose": premium,
            "change": 0.01,
            "changepercent": 0.5,
            "open": premium,
            "high": premium + 0.1,
            "low": premium - 0.1,
            "tick": 1,
        },
        "greeks": {
            "impvol": round(0.25 + distance, 4) if priced else 0.0,
            "delta": round(
                0.5 - distance if side == "Call" else -0.5 + distance,
                4,
            ),
            "gamma": 0.02,
            "theta": -0.01,
            "vega": 0.03,
            "rho": 0.001,
        },
        "key": {"symbol": [f"@AC{contract}:CA"]},
    }


GREEK_FIELDS = (
    "implied_volatility",
    "delta",
    "gamma",
    "theta",
    "vega",
    "rho",
)


def build_options_chain(
    priced: bool = True, greeks: bool = True, expired: bool = False
):
    """Validate a TMX options chain from a synthetic vendor payload.

    Parameters
    ----------
    priced : bool
        When False, every contract carries a zero implied volatility.
    greeks : bool
        When False, the chain is published without any greek columns, the way
        the end-of-day download is.
    expired : bool
        When True, the chain also carries a contract that has already expired,
        which the chain lists but leaves out of its frame.

    Returns
    -------
    TmxOptionsChainsData
        The validated chain.
    """
    from datetime import date, timedelta

    from openbb_tmx.models.options_chains import TmxOptionsChainsData, _flatten_chain

    today = date.today()
    index = 0
    groups: list = []
    tenors = (-7, *CHAIN_TENORS) if expired else CHAIN_TENORS

    for tenor in tenors:
        expiry = (today + timedelta(days=tenor)).isoformat()
        quotes: list = []

        for strike in CHAIN_STRIKES:
            for side in ("Call", "Put"):
                quotes.append(_contract_quote(expiry, strike, side, index, priced))
                index += 1

        groups.append({"expirydate": expiry, "callputgroup": [{"quote": quotes}]})

    flat = _flatten_chain({"expiryGroup": groups}, "AC")
    flat["underlying_price"] = [UNDERLYING_PRICE] * len(flat["contract_symbol"])

    if not greeks:
        for field in GREEK_FIELDS:
            flat.pop(field, None)

    return TmxOptionsChainsData.model_validate(flat)


@pytest.fixture
def options_chain():
    """Serve a validated TMX options chain."""
    return build_options_chain()
