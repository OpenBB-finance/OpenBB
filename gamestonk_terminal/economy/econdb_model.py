""" EconDB Model """
__docformat__ = "numpy"

import logging

logger = logging.getLogger(__name__)

COUNTRY_CODES = {
    {
        "Albania": "AL",
        "Argentina": "AR",
        "Australia": "AU",
        "Austria": "AT",
        "Azerbaijan": "AZ",
        "Bangladesh": "BD",
        "Belarus": "BY",
        "Belgium": "BE",
        "Bhutan": "BT",
        "Bosnia and Herzegovina": "BA",
        "Botswana": "BW",
        "Brazil": "BR",
        "Bulgaria": "BG",
        "Cambodia": "KH",
        "Cameroon": "CM",
        "Canada": "CA",
        "Chile": "CL",
        "China": "CN",
        "Colombia": "CO",
        "Croatia": "HR",
        "Cyprus": "CY",
        "Czech Republic": "CZ",
        "Denmark": "DK",
        "Dominican Republic": "DO",
        "Egypt": "EG",
        "Estonia": "EE",
        "Finland": "FI",
        "France": "FR",
        "Germany": "DE",
        "Greece": "GR",
        "Honduras": "HN",
        "Hong Kong": "HK",
        "Hungary": "HU",
        "India": "IN",
        "Indonesia": "ID",
        "Iran": "IR",
        "Ireland": "IE",
        "Israel": "IL",
        "Italy": "IT",
        "Japan": "JP",
        "Kazakhstan": "KZ",
        "Laos": "LA",
        "Latvia": "LV",
        "Lebanon": "LB",
        "Lithuania": "LT",
        "Luxembourg": "LU",
        "Macedonia": "MK",
        "Malaysia": "MY",
        "Malta": "MT",
        "Mexico": "MX",
        "Mongolia": "MN",
        "Netherlands": "NL",
        "New Zealand": "NZ",
        "Nigeria": "NG",
        "Norway": "NO",
        "Oman": "OM",
        "Pakistan": "PK",
        "Panama": "PA",
        "Peru": "PE",
        "Philippines": "PH",
        "Poland": "PL",
        "Portugal": "PT",
        "Qatar": "QA",
        "Romania": "RO",
        "Russia": "RU",
        "Saudi Arabia": "SA",
        "Serbia": "RS",
        "Singapore": "SG",
        "Slovakia": "SK",
        "Slovenia": "SI",
        "South Africa": "ZA",
        "South Korea": "KR",
        "Spain": "ES",
        "Sweden": "SE",
        "Switzerland": "CH",
        "Taiwan": "TW",
        "Thailand": "TH",
        "Tunisia": "TN",
        "Turkey": "TR",
        "Ukraine": "UA",
        "United Arab Emirates": "AE",
        "United States": "US",
        "Uzbekistan": "UZ",
        "Venezuela": "VE",
        "Vietnam": "VN",
    }
}


# @log_start_end(log=logger)
# def get_gdp(country: str, real: bool, period: str) -> pd.DataFrame:
#     """Get group (sectors, industry or country) valuation/performance data. [Source: Finviz]
#
#     Parameters
#     ----------
#     group : str
#        sectors, industry or country
#     data_type : str
#        valuation or performance
#
#     Returns
#     ----------
#     pd.DataFrame
#         dataframe with valuation/performance data
#     """
