"""Finance Database Model"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments,unexpected-keyword-arg

import logging
from typing import Optional

import financedatabase as fd
import yahooquery as yq
from requests.exceptions import ReadTimeout

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console, optional_rich_track

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_countries(industry: str = "", sector: str = "") -> list:
    """Get all countries in Yahoo Finance data based on sector or industry. [Source: Finance Database]

    Parameters
    ----------
    industry : str
        Filter retrieved countries by industry
    sector : str
        Filter retrieved countries by sector

    Returns
    -------
    list
        List of possible countries
    """
    # industry takes priority since there's 1 sector per industry, but multiple industries per sector
    equities = fd.Equities()

    if industry:
        return equities.search(industry=industry)["country"].dropna().unique()
    if sector:
        return equities.search(sector=sector)["country"].dropna().unique()

    return equities.select()["country"].dropna().unique()


@log_start_end(log=logger)
def get_sectors(industry: str = "", country: str = "") -> list:
    """Get all sectors in Yahoo Finance data based on country or industry. [Source: Finance Database]

    Parameters
    ----------
    industry : str
        Filter retrieved sectors by industry
    country : str
        Filter retrieved sectors by country

    Returns
    -------
    list
        List of possible sectors
    """
    # industry takes priority since there's 1 sector per industry, but multiple industries per country
    equities = fd.Equities()

    if industry:
        return equities.search(industry=industry)["sector"].dropna().unique()
    if country:
        return equities.search(country=country)["sector"].dropna().unique()

    return equities.select()["sector"].dropna().unique()


@log_start_end(log=logger)
def get_industries(country: str = "", sector: str = "") -> list:
    """Get all industries in Yahoo Finance data based on country or sector. [Source: Finance Database]

    Parameters
    ----------
    country : str
        Filter retrieved industries by countrys
    sector : str
        Filter retrieved industries by sector

    Returns
    -------
    list
        List of possible industries
    """
    equities = fd.Equities()

    if country and sector:
        return (
            equities.select(country=country, sector=sector)["industry"]
            .dropna()
            .unique()
        )

    if country:
        return equities.select(country=country)["industry"].dropna().unique()

    if sector:
        return equities.select(sector=sector)["industry"].dropna().unique()

    return equities.select()["industry"].dropna().unique()


@log_start_end(log=logger)
def get_marketcap() -> list:
    """Get all market cap division in Yahoo Finance data. [Source: Finance Database]

    Returns
    -------
    list
        List of possible market caps
    """
    return ["Small Cap", "Mid Cap", "Large Cap"]


@log_start_end(log=logger)
def filter_stocks(
    country: Optional[str] = None,
    sector: Optional[str] = None,
    industry: Optional[str] = None,
    marketcap: str = "",
    exclude_exchanges: bool = True,
) -> list:
    """Filter stocks based on country, sector, industry, market cap and exclude exchanges.
    [Source: Finance Database]

    Parameters
    ----------
    country: str
        Search by country to find stocks matching the criteria.
    sector: str
        Search by sector to find stocks matching the criteria.
    industry: str
        Search by industry to find stocks matching the criteria.
    marketcap: str
        Select stocks based on the market cap.
    exclude_exchanges: bool
        When you wish to include different exchanges use this boolean.

    Returns
    -------
    list
        List of filtered stocks
    """
    equities = fd.Equities()
    kwargs = {}
    if country:
        kwargs["country"] = country
    if sector:
        kwargs["sector"] = sector
    if industry:
        kwargs["industry"] = industry
    if marketcap:
        kwargs["market_cap"] = marketcap
    try:
        data = equities.search(exclude_exchanges=exclude_exchanges, **kwargs)

        return list(data.index)

    except ValueError as e:
        logger.exception(str(e))
        return []

    except ReadTimeout:
        console.print(
            "[red]Unable to retrieve company data from GitHub which limits the search"
            " capabilities. This tends to be due to access restrictions for GitHub.com,"
            " please check if you can access this website without a VPN.[/red]\n"
        )
        return []


def get_json(symbol: str) -> dict:
    """Get json data from Yahoo Finance for a given symbol.
    Code adapted from deprecated function `yfinance.utils.get_json`
    in version 0.1.96 of the yfinance package.

    Parameters
    ----------
    symbol : str
        Symbol to get data for

    Returns
    -------
    dict
        Dictionary of json data
    """

    data = dict()
    try:
        data["summaryProfile"] = yq.Ticker(symbol).summary_profile[symbol]
        return data
    except Exception:
        return data


@log_start_end(log=logger)
def get_stocks_data(
    country: str = "United States",
    sector: str = "Materials",
    industry: str = "Metals & Mining",
    marketcap: str = "Large Cap",
    exclude_exchanges: bool = True,
) -> dict:
    """Get stocks data based on country, sector, industry, market cap and exclude exchanges.
    [Source: Finance Database]

    Parameters
    ----------
    country: str
        Search by country to find stocks matching the criteria.
    sector: str
        Search by sector to find stocks matching the criteria.
    industry: str
        Search by industry to find stocks matching the criteria.
    marketcap: str
        Select stocks based on the market cap.
    exclude_exchanges: bool
        When you wish to include different exchanges use this boolean.

    Returns
    -------
    dict
        Dictionary of filtered stocks data
    """
    stocks = filter_stocks(country, sector, industry, marketcap, exclude_exchanges)

    stocks_data = {
        symbol: get_json(symbol=symbol) for symbol in optional_rich_track(stocks)
    }

    return stocks_data


@log_start_end(log=logger)
def get_companies_per_sector_in_country(
    country: str = "United States",
    mktcap: str = "Large",
    exclude_exchanges: bool = True,
) -> dict:
    """Get number of companies per sector in a specific country (and specific market cap). [Source: Finance Database]

    Parameters
    ----------
    country: str
        Select country to get number of companies by each sector
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges

    Returns
    -------
    dict
        Dictionary of sectors and number of companies in a specific country
    """
    equities = fd.Equities()
    companies_per_sector = {}

    for sector in optional_rich_track(get_sectors(country=country)):
        if sector:
            try:
                companies = equities.search(
                    country=country,
                    sector=sector,
                    exclude_exchanges=exclude_exchanges,
                    market_cap=f"{mktcap} Cap",
                )

                companies_per_sector[sector] = len(companies)
            except ValueError as e:
                logger.exception(str(e))

            except ReadTimeout:
                console.print(
                    "[red]Unable to retrieve company data from GitHub which limits the search"
                    " capabilities. This tends to be due to access restrictions for GitHub.com,"
                    " please check if you can access this website without a VPN.[/red]\n"
                )
                return {}

    return companies_per_sector


@log_start_end(log=logger)
def get_companies_per_industry_in_country(
    country: str = "United States",
    mktcap: str = "Large",
    exclude_exchanges: bool = True,
) -> dict:
    """Get number of companies per industry in a specific country (and specific market cap).
    [Source: Finance Database]

    Parameters
    ----------
    country: str
        Select country to get number of companies by each industry
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges

    Returns
    -------
    dict
        Dictionary of industries and number of companies in a specific country
    """
    equities = fd.Equities()
    companies_per_industry = {}

    for industry in optional_rich_track(get_industries(country=country)):
        if industry:
            try:
                companies = equities.search(
                    country=country,
                    industry=industry,
                    exclude_exchanges=exclude_exchanges,
                    market_cap=f"{mktcap} Cap",
                )

                companies_per_industry[industry] = len(companies)

            except ValueError as e:
                logger.exception(str(e))

            except ReadTimeout:
                console.print(
                    "[red]Unable to retrieve company data from GitHub which limits the search"
                    " capabilities. This tends to be due to access restrictions for GitHub.com,"
                    " please check if you can access this website without a VPN.[/red]\n"
                )
                return {}

    return companies_per_industry


@log_start_end(log=logger)
def get_companies_per_industry_in_sector(
    sector: str = "Technology",
    mktcap: str = "Large",
    exclude_exchanges: bool = True,
) -> dict:
    """Get number of companies per industry in a specific sector (and specific market cap).
    [Source: Finance Database]

    Parameters
    ----------
    sector: str
        Select sector to get number of companies by each industry
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges

    Returns
    -------
    dict
        Dictionary of industries and number of companies in a specific sector
    """
    equities = fd.Equities()
    companies_per_industry = {}
    for industry in optional_rich_track(get_industries(sector=sector)):
        if industry:
            try:
                companies = equities.search(
                    sector=sector,
                    industry=industry,
                    exclude_exchanges=exclude_exchanges,
                    market_cap=f"{mktcap} Cap",
                )

                companies_per_industry[industry] = len(companies)

            except ValueError as e:
                logger.exception(str(e))

            except ReadTimeout:
                console.print(
                    "[red]Unable to retrieve company data from GitHub which limits the search"
                    " capabilities. This tends to be due to access restrictions for GitHub.com,"
                    " please check if you can access this website without a VPN.[/red]\n"
                )
                return {}

    return companies_per_industry


@log_start_end(log=logger)
def get_companies_per_country_in_sector(
    sector: str = "Technology",
    mktcap: str = "Large",
    exclude_exchanges: bool = True,
) -> dict:
    """Get number of companies per country in a specific sector (and specific market cap).
    [Source: Finance Database]

    Parameters
    ----------
    sector: str
        Select sector to get number of companies by each country
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges

    Returns
    -------
    dict
        Dictionary of countries and number of companies in a specific sector
    """
    equities = fd.Equities()
    companies_per_country = {}
    for country in optional_rich_track(get_countries(sector=sector)):
        if country:
            try:
                companies = equities.search(
                    sector=sector,
                    country=country,
                    exclude_exchanges=exclude_exchanges,
                    market_cap=f"{mktcap} Cap",
                )

                companies_per_country[country] = len(companies)

            except ValueError as e:
                logger.exception(str(e))

            except ReadTimeout:
                console.print(
                    "[red]Unable to retrieve company data from GitHub which limits the search"
                    " capabilities. This tends to be due to access restrictions for GitHub.com,"
                    " please check if you can access this website without a VPN.[/red]\n"
                )
                return {}

    return companies_per_country


@log_start_end(log=logger)
def get_companies_per_country_in_industry(
    industry: str = "Metals & Mining",
    mktcap: str = "Large",
    exclude_exchanges: bool = True,
) -> dict:
    """Get number of companies per country in a specific industry (and specific market cap).
    [Source: Finance Database]

    Parameters
    ----------
    industry: str
        Select industry to get number of companies by each country
    mktcap: str
        Select market cap of companies to consider from Small, Mid and Large
    exclude_exchanges : bool
        Exclude international exchanges

    Returns
    -------
    dict
        Dictionary of countries and number of companies in a specific sector
    """
    equities = fd.Equities()
    companies_per_country = {}
    for country in optional_rich_track(get_countries(industry=industry)):
        if country:
            try:
                companies = equities.search(
                    industry=industry,
                    country=country,
                    exclude_exchanges=exclude_exchanges,
                    market_cap=f"{mktcap} Cap",
                )

                companies_per_country[country] = len(companies)

            except ValueError as e:
                logger.exception(str(e))

            except ReadTimeout:
                console.print(
                    "[red]Unable to retrieve company data from GitHub which limits the search"
                    " capabilities. This tends to be due to access restrictions for GitHub.com,"
                    " please check if you can access this website without a VPN.[/red]\n"
                )
                return {}

    return companies_per_country
