"""Finance Database Model"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments,unexpected-keyword-arg

import logging
from typing import Optional

import financedatabase as fd
import yfinance as yf
from requests.exceptions import ReadTimeout
from tqdm import tqdm

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

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
    if industry:
        return fd.show_options("equities", industry=True)[industry]["Countries"]
    if sector:
        return fd.show_options("equities", sector=sector)["Countries"]

    return [count for count in fd.show_options("equities", "countries") if count]


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
    if industry:
        return [fd.show_options("equities", industry=True)[industry]["Sector"]]
    if country:
        return fd.show_options("equities", country=country)["Sectors"]

    return [sect for sect in fd.show_options("equities", "sectors") if sect]


@log_start_end(log=logger)
def get_industries(country: str = "", sector: str = "") -> list:
    """Get all industries in Yahoo Finance data based on country or sector. [Source: Finance Database]

    Parameters
    ----------
    country : str
        Filter retrieved industries by country
    sector : str
        Filter retrieved industries by sector

    Returns
    -------
    list
        List of possible industries
    """
    if country and sector:
        return fd.show_options("equities", country=country, sector=sector)

    if country:
        return fd.show_options("equities", country=country)["Industries"]

    if sector:
        return fd.show_options("equities", sector=sector)["Industries"]

    return [ind for ind in fd.show_options("equities", "industries") if ind]


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
    kwargs = {}
    if country:
        kwargs["country"] = country
    if sector:
        kwargs["sector"] = sector
    if industry:
        kwargs["industry"] = industry
    try:
        data = fd.select_equities(exclude_exchanges=exclude_exchanges, **kwargs)

        if marketcap:
            data = fd.search_products(data, query=marketcap, search="market_cap")

        return list(data.keys())

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

    data_stores = yf.data.TickerData(symbol).get_json_data_stores()

    if "QuoteSummaryStore" not in data_stores:
        # Problem in data. Either delisted, or Yahoo spam triggered
        return {}

    data = data_stores["QuoteSummaryStore"]
    # add data about Shares Outstanding for companies' tickers if they are available
    try:
        data["annualBasicAverageShares"] = data_stores["QuoteTimeSeriesStore"][
            "timeSeries"
        ]["annualBasicAverageShares"]
    except Exception:
        pass

    return data


@log_start_end(log=logger)
def get_stocks_data(
    country: str = "United States",
    sector: str = "Communication Services",
    industry: str = "Internet Content & Information",
    marketcap: str = "Mega Cap",
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

    stocks_data = {symbol: get_json(symbol=symbol) for symbol in tqdm(stocks)}

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
    companies_per_sector = {}

    for sector in tqdm(get_sectors(country=country)):
        if sector:
            try:
                companies = fd.select_equities(
                    country=country, sector=sector, exclude_exchanges=exclude_exchanges
                )
                if mktcap:
                    companies = fd.search_products(
                        companies, query=mktcap + " Cap", search="market_cap"
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
    companies_per_industry = {}

    for industry in tqdm(get_industries(country=country)):
        if industry:
            try:
                companies = fd.select_equities(
                    country=country,
                    industry=industry,
                    exclude_exchanges=exclude_exchanges,
                )
                if mktcap:
                    companies = fd.search_products(
                        companies, query=mktcap + " Cap", search="market_cap"
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
    sector: str = "Technology", mktcap: str = "Large", exclude_exchanges: bool = True
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
    companies_per_industry = {}
    for industry in tqdm(get_industries(sector=sector)):
        if industry:
            try:
                companies = fd.select_equities(
                    sector=sector,
                    industry=industry,
                    exclude_exchanges=exclude_exchanges,
                )
                if mktcap:
                    companies = fd.search_products(
                        companies, query=mktcap + " Cap", search="market_cap"
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
    sector: str = "Technology", mktcap: str = "Large", exclude_exchanges: bool = True
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
    companies_per_country = {}
    for country in tqdm(get_countries(sector=sector)):
        if country:
            try:
                companies = fd.select_equities(
                    sector=sector,
                    country=country,
                    exclude_exchanges=exclude_exchanges,
                )
                if mktcap:
                    companies = fd.search_products(
                        companies, query=mktcap + " Cap", search="market_cap"
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
    industry: str = "Internet Content & Information",
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
    companies_per_country = {}
    for country in tqdm(get_countries(industry=industry)):
        if country:
            try:
                companies = fd.select_equities(
                    industry=industry,
                    country=country,
                    exclude_exchanges=exclude_exchanges,
                )
                if mktcap:
                    companies = fd.search_products(
                        companies, query=mktcap + " Cap", search="market_cap"
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
