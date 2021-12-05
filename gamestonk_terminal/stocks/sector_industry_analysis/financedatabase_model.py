"""Finance Database Model"""
__docformat__ = "numpy"
# pylint:disable=too-many-arguments,unexpected-keyword-arg

from tqdm import tqdm
import financedatabase as fd
import yfinance as yf


def get_countries(industry: str = "", sector: str = ""):
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
    return fd.show_options("equities", "countries")


def get_sectors(industry: str = "", country: str = ""):
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

    return fd.show_options("equities", "sectors")


def get_industries(country: str = "", sector: str = ""):
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

    return fd.show_options("equities", "industries")


def get_marketcap():
    """Get all market cap division in Yahoo Finance data. [Source: Finance Database]

    Returns
    -------
    list
        List of possible market caps
    """
    return list(["Small Cap", "Mid Cap", "Large Cap"])


def filter_stocks(
    country: str,
    sector: str,
    industry: str,
    marketcap: str = "",
    exclude_exchanges: bool = True,
):
    """Filter stocks based on country, sector, industry, market cap and exclude exchanges. [Source: Finance Database]

    Parameters
    ----------
    country: str
        Search by country to find stocks matching the criteria.
    sector : str
        Search by sector to find stocks matching the criteria.
    industry : str
        Search by industry to find stocks matching the criteria.
    marketcap : str
        Select stocks based on the market cap.
    exclude_exchanges: bool
        When you wish to include different exchanges use this boolean.

    Returns
    -------
    list
        List of filtered stocks
    """
    try:
        if country:
            if sector:
                if industry:
                    data = fd.select_equities(
                        country=country,
                        sector=sector,
                        industry=industry,
                        exclude_exchanges=exclude_exchanges,
                    )
                else:  # no industry
                    data = fd.select_equities(
                        country=country,
                        sector=sector,
                        exclude_exchanges=exclude_exchanges,
                    )
            else:  # no sector
                if industry:
                    data = fd.select_equities(
                        country=country,
                        industry=industry,
                        exclude_exchanges=exclude_exchanges,
                    )
                else:  # no industry
                    data = fd.select_equities(
                        country=country,
                        exclude_exchanges=exclude_exchanges,
                    )

        else:  # no country
            if sector:
                if industry:
                    data = fd.select_equities(
                        sector=sector,
                        industry=industry,
                        exclude_exchanges=exclude_exchanges,
                    )
                else:  # no industry
                    data = fd.select_equities(
                        sector=sector,
                        exclude_exchanges=exclude_exchanges,
                    )
            else:  # no sector
                if industry:
                    data = fd.select_equities(
                        industry=industry,
                        exclude_exchanges=exclude_exchanges,
                    )
                else:  # no industry
                    data = {}

        if marketcap:
            data = fd.search_products(data, query=marketcap, search="market_cap")

        return list(data.keys())

    except ValueError:
        return list()


def get_stocks_data(
    country: str,
    sector: str,
    industry: str,
    marketcap: str = "",
    exclude_exchanges: bool = True,
):
    """Get stocks data based on country, sector, industry, market cap and exclude exchanges. [Source: Finance Database]

    Parameters
    ----------
    country: str
        Search by country to find stocks matching the criteria.
    sector : str
        Search by sector to find stocks matching the criteria.
    industry : str
        Search by industry to find stocks matching the criteria.
    marketcap : str
        Select stocks based on the market cap.
    exclude_exchanges: bool
        When you wish to include different exchanges use this boolean.

    Returns
    -------
    dict
        Dictionary of filtered stocks data
    """
    stocks = filter_stocks(country, sector, industry, marketcap, exclude_exchanges)

    stocks_data = {}
    for symbol in tqdm(stocks):
        stocks_data[symbol] = yf.utils.get_json(
            f"https://finance.yahoo.com/quote/{symbol}"
        )

    return stocks_data


def get_companies_per_sector_in_country(
    country: str, mktcap: str = "", exclude_exchanges: bool = True
):
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
            except ValueError:
                pass

    return companies_per_sector


def get_companies_per_industry_in_country(
    country: str, mktcap: str = "", exclude_exchanges: bool = True
):
    """Get number of companies per industry in a specific country (and specific market cap). [Source: Finance Database]

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

            except ValueError:
                pass

    return companies_per_industry


def get_companies_per_industry_in_sector(
    sector: str, mktcap: str = "", exclude_exchanges: bool = True
):
    """Get number of companies per industry in a specific sector (and specific market cap). [Source: Finance Database]

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

            except ValueError:
                pass

    return companies_per_industry


def get_companies_per_country_in_sector(
    sector: str, mktcap: str = "", exclude_exchanges: bool = True
):
    """Get number of companies per country in a specific sector (and specific market cap). [Source: Finance Database]

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

            except ValueError:
                pass

    return companies_per_country


def get_companies_per_country_in_industry(
    industry: str, mktcap: str = "", exclude_exchanges: bool = True
):
    """Get number of companies per country in a specific industry (and specific market cap). [Source: Finance Database]

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

            except ValueError:
                pass

    return companies_per_country
