"""BlackRock ETF Data"""

from datetime import timedelta
from io import StringIO
from typing import Dict, Literal

import pandas as pd
import requests_cache

blackrock_america_products = requests_cache.CachedSession(
    "OpenBB_Blackrock_America_Products",
    expire_after=timedelta(days=1),
    use_cache_dir=True,
)

blackrock_canada_products = requests_cache.CachedSession(
    "OpenBB_Blackrock_Canada_Products",
    expire_after=timedelta(days=1),
    use_cache_dir=True,
)

blackrock_canada_holdings = requests_cache.CachedSession(
    "OpenBB_Blackrock_Canada_Holdings",
    expire_after=timedelta(days=1),
    use_cache_dir=True,
)

blackrock_america_holdings = requests_cache.CachedSession(
    "OpenBB_Blackrock_America_Holdings",
    expire_after=timedelta(days=1),
    use_cache_dir=True,
)

blackrock_canada_historical_holdings = requests_cache.CachedSession(
    "OpenBB_Blackrock_Canada_Historical_Holdings",
    expire_after=timedelta(days=30),
    use_cache_dir=True,
)

blackrock_america_historical_holdings = requests_cache.CachedSession(
    "OpenBB_Blackrock_America_Historical_Holdings",
    expire_after=timedelta(days=30),
    use_cache_dir=True,
)


COUNTRIES = Literal["america", "canada"]

CANADA_COLUMNS = [
    "portfolioId",
    "symbol",
    "fundName",
    "inceptionDate",
    "aladdinCountry",
    "aladdinAssetClass",
    "aladdinSubAssetClass",
    "aladdinRegion",
    "aladdinMarketType",
    "investmentStyle",
    "aladdinStrategy",
    "premiumDiscount",
    "distYield",
    "twelveMonTrlYield",
    "weightedAvgYieldToMaturity",
    "unsubsidizedYield",
    "thirtyDaySecYield",
    "totalNetAssets",
    "navYearToDate",
    "navOneYearAnnualized",
    "navThreeYearAnnualized",
    "navFiveYearAnnualized",
    "navSinceInceptionAnnualized",
    "mer",
    "productPageUrl",
]

AMERICA_COLUMNS = [
    "portfolioId",
    "symbol",
    "fundName",
    "inceptionDate",
    "cusip",
    "isin",
    "sedol",
    "aladdinAssetClass",
    "aladdinSubAssetClass",
    "aladdinEsgClassification",
    "aladdinRegion",
    "aladdinCountry",
    "aladdinMarketType",
    "investmentStyle",
    "productType",
    "productRange",
    "fees",
    "mgt",
    "ter",
    "netr",
    "dailyPerformanceYearToDate",
    "thirtyDaySecYield",
    "twelveMonTrlYield",
    "weightedAvgYieldToMaturity",
    "yieldToWorst",
    "cleanDuration",
    "effectiveDuration",
    "optionAdjustedSpread",
    "priceOneYearAnnualized",
    "priceThreeYearAnnualized",
    "priceFiveYearAnnualized",
    "priceTenYearAnnualized",
    "priceYearToDate",
    "priceSinceInceptionAnnualized",
    "quarterlyPriceYearToDate",
    "quarterlyPriceOneYearAnnualized",
    "quarterlyPriceThreeYearAnnualized",
    "quarterlyPriceFiveYearAnnualized",
    "quarterlyPriceTenYearAnnualized",
    "quarterlyPriceSinceInceptionAnnualized",
    "totalNetAssets",
    "navAmount",
    "navYearToDate",
    "navOneYearAnnualized",
    "navThreeYearAnnualized",
    "navFiveYearAnnualized",
    "navTenYearAnnualized",
    "navSinceInceptionAnnualized",
    "quarterlyNavYearToDate",
    "quarterlyNavOneYearAnnualized",
    "quarterlyNavThreeYearAnnualized",
    "quarterlyNavFiveYearAnnualized",
    "quarterlyNavTenYearAnnualized",
    "quarterlyNavSinceInceptionAnnualized",
    "esgCoverage",
    "esgMsciQualityScore",
    "esgRating",
    "wtdAvgCarbonIntensity",
    "productPageUrl",
]


def camel_to_snake(str):
    """Convert camelCase to snake_case."""
    return "".join(["_" + i.lower() if i.isupper() else i for i in str]).lstrip("_")


def clean_data(etfs: pd.DataFrame) -> pd.DataFrame:  # noqa
    clean_columns = ["navAmount", "inceptionDate"]
    for column in clean_columns:
        if column in etfs.columns:
            df = etfs[column]
            new_data = []
            for i in df.index:
                if df.iloc[i] is not None:
                    new_data.append(df.iloc[i]["r"])
            etfs[column] = new_data

    nav = []
    nav1y = []
    nav3y = []
    nav5y = []
    nav10y = []
    nav_inception = []
    nav_ytd = []
    q_nav1y = []
    q_nav3y = []
    q_nav5y = []
    q_nav10y = []
    q_nav_inception = []
    q_nav_ytd = []
    ytm = []
    ttm_yield = []
    premium_discount = []
    mer = []
    dist_yield = []
    daily_performance = []
    esg_coverage = []
    esg_msci = []
    fees = []
    mgt = []
    netr = []
    ter = []
    ter_ocf = []
    oas = []
    sec_yield = []
    unsubsidized_yield = []
    carbon = []
    total_net_assets = []
    price1y = []
    price3y = []
    price5y = []
    price10y = []
    priceytd = []
    priceincep = []
    q_price1y = []
    q_price3y = []
    q_price5y = []
    q_price10y = []
    q_price_inception = []
    q_price_ytd = []
    yield_to_worst = []
    effective_duration = []
    clean_duration = []

    for i in etfs.index:
        nav.append(dict(etfs.totalNetAssets.loc[i]).get("r"))
        nav1y.append(dict(etfs.navOneYearAnnualized.loc[i]).get("r"))
        nav3y.append(dict(etfs.navThreeYearAnnualized.loc[i]).get("r"))
        nav5y.append(dict(etfs.navFiveYearAnnualized.loc[i]).get("r"))

        if "esgCoverage" in etfs.columns:
            esg_coverage.append(dict(etfs.esgCoverage.loc[i]).get("r"))
            esg_msci.append(dict(etfs.esgMsciQualityScore.loc[i]).get("r"))
            fees.append(dict(etfs.fees.loc[i]).get("r"))
            mgt.append(dict(etfs.mgt.loc[i]).get("r"))
            netr.append(dict(etfs.netr.loc[i]).get("r"))
            ter.append(dict(etfs.ter.loc[i]).get("r"))
            ter_ocf.append(dict(etfs.ter_ocf.loc[i]).get("r"))
            oas.append(dict(etfs.optionAdjustedSpread.loc[i]).get("r"))
            carbon.append(dict(etfs.wtdAvgCarbonIntensity.loc[i]).get("r"))

        if "dailyPerformanceYearToDate" in etfs.columns:
            daily_performance.append(
                dict(etfs.dailyPerformanceYearToDate.loc[i]).get("r")
            )
            total_net_assets.append(dict(etfs.totalNetAssetsFund.loc[i]).get("r"))

        if "thirtyDaySecYield" in etfs.columns:
            if etfs.thirtyDaySecYield.loc[i] is not None:
                sec_yield.append(dict(etfs.thirtyDaySecYield.loc[i]).get("r"))
            else:
                sec_yield.append(None)

        if "distYield" in etfs.columns:
            if etfs.distYield.loc[i] is not None:
                dist_yield.append(dict(etfs.distYield.loc[i]).get("r"))
            else:
                dist_yield.append(None)

        if "yieldToWorst" in etfs.columns:
            if etfs.yieldToWorst.loc[i] is not None:
                yield_to_worst.append(dict(etfs.yieldToWorst.loc[i]).get("r"))
            else:
                yield_to_worst.append(None)

        if "effectiveDuration" in etfs.columns:
            if etfs.effectiveDuration.iloc[i] is not None:
                effective_duration.append(dict(etfs.effectiveDuration.iloc[i]).get("r"))
            else:
                yield_to_worst.append(None)

        if "cleanDuration" in etfs.columns:
            if etfs.cleanDuration.iloc[i] is not None:
                clean_duration.append(dict(etfs.cleanDuration.iloc[i]).get("r"))
            else:
                clean_duration.append(None)

        if "mer" in etfs.columns:
            mer.append(dict(etfs.mer.loc[i]).get("r"))

        if "premiumDiscount" in etfs.columns:
            premium_discount.append(dict(etfs.premiumDiscount.loc[i]).get("r"))

        if "navTenYearAnnualized" in etfs.columns:
            nav10y.append(dict(etfs.navTenYearAnnualized.loc[i]).get("r"))

        if "quarterlyPriceOneYearAnnualized" in etfs.columns:
            q_price_ytd.append(dict(etfs.quarterlyPriceYearToDate.loc[i]).get("r"))
            q_price1y.append(dict(etfs.quarterlyPriceOneYearAnnualized.loc[i]).get("r"))
            q_price3y.append(
                dict(etfs.quarterlyPriceThreeYearAnnualized.loc[i]).get("r")
            )
            q_price5y.append(
                dict(etfs.quarterlyPriceFiveYearAnnualized.loc[i]).get("r")
            )
            q_price10y.append(
                dict(etfs.quarterlyPriceTenYearAnnualized.loc[i]).get("r")
            )
            q_price_inception.append(
                dict(etfs.quarterlyPriceSinceInceptionAnnualized.loc[i]).get("r")
            )
            q_nav_ytd.append(dict(etfs.quarterlyNavYearToDate.loc[i]).get("r"))
            q_nav1y.append(dict(etfs.quarterlyNavOneYearAnnualized.loc[i]).get("r"))
            q_nav3y.append(dict(etfs.quarterlyNavThreeYearAnnualized.loc[i]).get("r"))
            q_nav5y.append(dict(etfs.quarterlyNavFiveYearAnnualized.loc[i]).get("r"))
            q_nav10y.append(dict(etfs.quarterlyNavTenYearAnnualized.loc[i]).get("r"))
            q_nav_inception.append(
                dict(etfs.quarterlyNavSinceInceptionAnnualized.loc[i]).get("r")
            )

        if etfs.priceYearToDate.loc[i] is not None:
            priceytd.append(dict(etfs.priceYearToDate.loc[i]).get("r"))
        else:
            priceytd.append(None)

        if etfs.priceOneYearAnnualized.loc[i] is not None:
            price1y.append(dict(etfs.priceOneYearAnnualized.loc[i]).get("r"))
        else:
            price1y.append(None)

        if etfs.priceThreeYearAnnualized.loc[i] is not None:
            price3y.append(dict(etfs.priceThreeYearAnnualized.loc[i]).get("r"))
        else:
            price3y.append(None)

        if etfs.priceFiveYearAnnualized.loc[i] is not None:
            price5y.append(dict(etfs.priceFiveYearAnnualized.loc[i]).get("r"))
        else:
            price5y.append(None)

        if etfs.priceTenYearAnnualized.loc[i] is not None:
            price10y.append(dict(etfs.priceTenYearAnnualized.loc[i]).get("r"))
        else:
            price10y.append(None)

        if etfs.priceSinceInceptionAnnualized.loc[i] is not None:
            priceincep.append(dict(etfs.priceSinceInceptionAnnualized.loc[i]).get("r"))
        else:
            priceincep.append(None)

        if etfs.navSinceInceptionAnnualized.loc[i] is not None:
            nav_inception.append(dict(etfs.navSinceInceptionAnnualized.loc[i]).get("r"))
        else:
            nav_inception.append(None)

        if etfs.navYearToDate.loc[i] is not None:
            nav_ytd.append(dict(etfs.navYearToDate.loc[i]).get("r"))
        else:
            nav_ytd.append(None)

        if etfs.weightedAvgYieldToMaturity.loc[i] is not None:
            ytm.append(dict(etfs.weightedAvgYieldToMaturity.loc[i]).get("r"))
        else:
            ytm.append(None)

        if etfs.twelveMonTrlYield.loc[i] is not None:
            ttm_yield.append(dict(etfs.twelveMonTrlYield.loc[i]).get("r"))
        else:
            ttm_yield.append(None)

        if etfs.unsubsidizedYield.loc[i] is not None:
            unsubsidized_yield.append(dict(etfs.unsubsidizedYield.loc[i]).get("r"))
        else:
            unsubsidized_yield.append(None)

    if len(set(priceincep)) > 1:
        etfs["priceSinceInceptionAnnualized"] = priceincep

    if len(set(priceytd)) > 1:
        etfs["priceYearToDate"] = priceytd

    if len(set(price1y)) > 1:
        etfs["priceOneYearAnnualized"] = price1y

    if len(set(price3y)) > 1:
        etfs["priceThreeYearAnnualized"] = price3y

    if len(set(price5y)) > 1:
        etfs["priceFiveYearAnnualized"] = price5y

    if len(set(price10y)) > 1:
        etfs["priceTenYearAnnualized"] = price10y

    if "quarterlyPriceOneYearAnnualized" in etfs.columns:
        etfs["quarterlyPriceYearToDate"] = q_price_ytd
        etfs["quarterlyPriceOneYearAnnualized"] = q_price1y
        etfs["quarterlyPriceThreeYearAnnualized"] = q_price3y
        etfs["quarterlyPriceFiveYearAnnualized"] = q_price5y
        etfs["quarterlyPriceTenYearAnnualized"] = q_price10y
        etfs["quarterlyPriceSinceInceptionAnnualized"] = q_price_inception
        etfs["quarterlyNavYearToDate"] = q_nav_ytd
        etfs["quarterlyNavOneYearAnnualized"] = q_nav1y
        etfs["quarterlyNavThreeYearAnnualized"] = q_nav3y
        etfs["quarterlyNavFiveYearAnnualized"] = q_nav5y
        etfs["quarterlyNavTenYearAnnualized"] = q_nav10y
        etfs["quarterlyNavSinceInceptionAnnualized"] = q_nav_inception

    etfs["totalNetAssets"] = nav
    etfs["navYearToDate"] = nav_ytd
    etfs["navOneYearAnnualized"] = nav1y
    etfs["navThreeYearAnnualized"] = nav3y
    etfs["navFiveYearAnnualized"] = nav5y
    etfs["navSinceInceptionAnnualized"] = nav_inception
    etfs["weightedAvgYieldToMaturity"] = ytm
    etfs["twelveMonTrlYield"] = ttm_yield
    etfs["unsubsidizedYield"] = unsubsidized_yield

    if "dailyPerformanceYearToDate" in etfs.columns:
        etfs["dailyPerformanceYearToDate"] = daily_performance
        etfs["totalNetAssetsFund"] = total_net_assets

    if "premiumDiscount" in etfs.columns:
        etfs["premiumDiscount"] = premium_discount

    if "navTenYearAnnualized" in etfs.columns:
        etfs["navTenYearAnnualized"] = nav10y

    if "mer" in etfs.columns:
        etfs["mer"] = mer

    if "distYield" in etfs.columns:
        etfs["distYield"] = dist_yield

    if "thirtyDaySecYield" in etfs.columns:
        etfs["thirtyDaySecYield"] = sec_yield

    if "esgCoverage" in etfs.columns:
        etfs["esgCoverage"] = esg_coverage
        etfs["esgMsciQualityScore"] = esg_msci
        etfs["fees"] = fees
        etfs["mgt"] = mgt
        etfs["netr"] = netr
        etfs["ter"] = ter
        etfs["ter_ocf"] = ter_ocf
        etfs["optionAdjustedSpread"] = oas
        etfs["wtdAvgCarbonIntensity"] = carbon

    if "yieldToWorst" in etfs.columns:
        etfs["yieldToWorst"] = yield_to_worst
        etfs["effectiveDuration"] = effective_duration
        etfs["cleanDuration"] = clean_duration
    return etfs


class America:
    @staticmethod
    def get_all_etfs():
        """Gets all Blackrock US ETFs."""

        r = blackrock_america_products.get(
            "https://www.ishares.com/us/product-screener/product-screener-v3.1.jsn?dcrPath=/templatedata/config/product-screener-v3/data/en/us-ishares/ishares-product-screener-backend-config&siteEntryPassthrough=true"
        )
        if r.status_code != 200:
            raise RuntimeError(r.status_code)

        etfs = pd.DataFrame(r.json()).transpose().reset_index()

        etfs = etfs.rename(columns={"localExchangeTicker": "symbol"}).replace("-", "")

        etfs = clean_data(etfs)

        return etfs[AMERICA_COLUMNS].convert_dtypes()

    @staticmethod
    def generate_holdings_url(symbol: str, date: str = "") -> str:
        """Generates the URL for the Blackrock US ETF holdings."""
        symbol = symbol.upper()
        etfs = America.get_all_etfs()
        product_page_url = etfs[etfs["symbol"] == symbol].iloc[0].get("productPageUrl")
        url = (
            f"https://www.ishares.com{product_page_url}/1467271812596.ajax?fileType=csv"
        )
        if date:
            date = date.replace("-", "")
            url = url + f"&asOfDate={date}"
        url = url + f"&fileName={symbol.lower()}_holdings&dataType=fund"

        return url


class Canada:
    @staticmethod
    def get_all_etfs():
        """Gets all Blackrock Canada ETFs."""

        r = blackrock_canada_products.get(
            "https://www.blackrock.com/ca/investors/en/product-screener/product-screener-v3.jsn?dcrPath=/templatedata/config/product-screener-v3/data/en/ca-one/ca-one&siteEntryPassthrough=true"
        )
        if r.status_code != 200:
            raise RuntimeError(r.status_code)

        columns = r.json()["data"]["tableData"]["columns"]
        column_names = []
        for column in columns:
            column_names.append(column["name"])

        etfs = pd.DataFrame.from_records(r.json()["data"]["tableData"]["data"])
        etfs.columns = column_names
        etfs = etfs.rename(columns={"localExchangeTicker": "symbol"}).replace("-", "")

        etfs = clean_data(etfs)

        return etfs[CANADA_COLUMNS].convert_dtypes()

    @staticmethod
    def generate_holdings_url(symbol: str, date: str = "") -> str:
        """Generates the URL for the Blackrock Canada ETF holdings."""

        symbol = symbol.upper()
        date = date.replace("-", "") if date else ""
        etfs = Canada.get_all_etfs()
        portfolioID = etfs[etfs["symbol"] == symbol]["portfolioId"].iloc[0]
        symbol = symbol.replace(".", "")

        url = f"https://www.blackrock.com/ca/investors/en/products/{portfolioID}/fund/1464253357814.ajax?fileType=csv"
        if date:
            url = url + f"&asOfDate={date}"

        url = url + f"&fileName={symbol}_holdings&dataType=fund"

        return url


def extract_from_holdings(
    symbol: str,
    to_extract: Literal["sector", "country"] = "sector",
    country: COUNTRIES = "america",
    date: str = "",
) -> Dict:
    """Extracts target data from Blackrock ETF holdings data.  Supports: ['sector', 'country']."""

    data = {}
    if ".TO" in symbol or country == "canada":
        symbol = symbol.replace(".TO", "")  # noqa
        country = "canada"
    _etfs = America.get_all_etfs() if country == "america" else Canada.get_all_etfs()
    if symbol in _etfs["symbol"].to_list():
        if not date:
            r = (
                blackrock_america_holdings.get(
                    url=America.generate_holdings_url(symbol, date),  # type: ignore
                )
                if country == "america"
                else blackrock_canada_holdings.get(
                    url=Canada.generate_holdings_url(symbol, date),  # type: ignore
                )
            )
        if date:
            r = (
                blackrock_america_historical_holdings.get(
                    url=America.generate_holdings_url(symbol, date),  # type: ignore
                )
                if country == "america"
                else blackrock_canada_historical_holdings.get(
                    url=Canada.generate_holdings_url(symbol, date),  # type: ignore
                )
            )
        if r.status_code != 200:  # type: ignore
            raise RuntimeError(
                "Error with Blackrock endpoint ->" + str(r.status_code)  # type: ignore
            )

        indexed = pd.read_csv(StringIO(r.text), usecols=[0])  # type: ignore
        target = "Ticker" if "Name" not in indexed.iloc[:, 0].to_list() else "Name"
        idx = []
        idx = indexed[indexed.iloc[:, 0] == target].index.tolist()
        idx_value = idx[1] if len(idx) > 1 else idx[0]
        _holdings = pd.read_csv(
            StringIO(r.text), header=idx_value, thousands=","  # type: ignore
        )
        _holdings = _holdings.reset_index()
        columns = _holdings.iloc[0, :].values.tolist()
        _holdings.columns = columns
        holdings = (
            _holdings.iloc[1:-1, :] if country == "canada" else _holdings.iloc[1:-2, :]
        )
        holdings = holdings.convert_dtypes().fillna("0")

        holdings = holdings.rename(
            columns={
                "Name": "name",
                "Weight (%)": "weight",
                "Sector": "sector",
                "Location of Risk": "country",
                "Location": "country",
            }
        )
        if to_extract in holdings.columns.to_list():
            _target = holdings[["name", to_extract, "weight"]]
            _target.loc[:, "weight"] = _target["weight"].astype(float)
            target = _target.groupby(to_extract)[["weight"]].sum()
            target = target.rename(
                index={
                    "Telecommunication Services": "Communication Services",
                    "Telecommunications": "Communication Services",
                    "Materials & Processing": "Materials",
                    "Producer Durables": "Industrials",
                    "-": "other",
                    "Korea (South)": "South Korea",
                }
            )
            target.index = (
                target.index.str.replace("/", "")
                .str.replace("non-_", "non_")
                .str.replace("andor", "and")
            )
            for i in target.index:
                data.update({i: target.loc[i]["weight"]})

    return data
