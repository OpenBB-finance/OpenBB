"""Constants for the FINRA data services."""

from typing import Literal

QUERY_API_URL = "https://api.finra.org"
QUERY_API_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
QUERY_API_PAGE_LIMIT = 5000

TRACE_URL = (
    "https://services-dynarep.ddwa.finra.org/public/reporting/v2/data/group/"
    "FixedIncomeMarket/name"
)
TRACE_ORIGIN = "https://www.finra.org"
TRACE_REFERER = "https://www.finra.org/finra-data/fixed-income/corp-and-agency/trade"
TRACE_PAGE_LIMIT = 5000
TRACE_CONCURRENCY = 15
TRACE_ATTEMPTS = 3
TRACE_BACKOFF = 0.5
TRACE_RETRY_CODES = (502, 503, 524)

MARKET_DATA_URL = "https://finra-markets.morningstar.com"
MARKET_DATA_SDK_VERSION = "2.63.2"
SECURITY_TYPE_CONDITIONS = {
    "all": "ST,FE,FC,FO",
    "stock": "ST",
    "etf": "FE",
    "closed_end_fund": "FC",
    "mutual_fund": "FO",
}
MARKET_DATA_DETAIL_URL = f"{MARKET_DATA_URL}/MarketData/EquityOptions/detail.jsp"
LOOKUP_ATTEMPTS = 4
LOOKUP_THROTTLE_WAIT = 30
SECURITY_LIST_TYPES = {"stock": "ST", "etf": "FE", "closed_end_fund": "FC"}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 60

NA_TOKENS = ("", "-", "NA", "N/A")

BondTypes = Literal["CA", "TS", "TBA", "MBS", "ABS", "CMO"]

BOND_TYPES: dict[str, dict] = {
    "CA": {
        "label": "Corporate & Agency",
        "dataset": "corporateAndAgencySecurities",
        "fields": [
            "finraSecurityIdentifier",
            "cusip",
            "issueSymbolIdentifier",
            "issuerName",
            "productSubTypeCode",
            "couponRate",
            "couponType",
            "maturityDate",
            "isPerpetual",
            "isCallable",
            "nextCallDate",
            "isConvertible",
            "is144A",
            "industryGroup",
            "traceGradeCode",
            "moodysRating",
            "moodyRatingDate",
            "standardAndPoorsRating",
            "standardAndPoorsRatingDate",
            "lastSalePrice",
            "lastSaleYield",
            "lastTradeDate",
            "priceChangeNumber",
            "priceChangePercent",
        ],
    },
    "TS": {
        "label": "U.S. Treasury",
        "dataset": "treasurySecurities",
        "fields": [
            "finraSecurityIdentifier",
            "cusip",
            "issueSymbolIdentifier",
            "issuerName",
            "productSubTypeCode",
            "securityDescription",
            "benchmarkTermCode",
            "couponRate",
            "couponType",
            "maturityDate",
            "traceGradeCode",
            "priceType",
            "lastSalePrice",
            "lastSaleYield",
            "lastTradeDate",
            "lastTradeTime",
            "priceChangeNumber",
            "priceChangePercent",
        ],
    },
    "TBA": {
        "label": "To-Be-Announced MBS",
        "dataset": "tbaSecurities",
        "fields": [
            "finraSecurityIdentifier",
            "cusip",
            "issueSymbolIdentifier",
            "productSubTypeCode",
            "subProductType",
            "issuingAgency",
            "couponRate",
            "couponType",
            "settlementDateMonth",
            "lastSalePrice",
            "lastTradeDate",
            "priceChangeNumber",
            "priceChangePercent",
        ],
    },
    "MBS": {
        "label": "Mortgage-Backed Securities",
        "dataset": "mortgageBackedSecurities",
        "fields": [
            "finraSecurityIdentifier",
            "cusip",
            "issueSymbolIdentifier",
            "productSubTypeCode",
            "subProductType",
            "issuingAgency",
            "poolNumber",
            "referenceDataIdentifier",
            "mortgageProduct",
            "amortizationType",
            "couponRate",
            "maturityDate",
            "originalMaturityTerm",
            "weightedAverageCoupon",
            "weightedAverageMaturity",
            "weightedAverageLoanAge",
            "loanToValueRatio",
            "averageLoanSize",
            "lastSalePrice",
            "lastTradeDate",
            "priceChangeNumber",
            "priceChangePercent",
        ],
    },
    "ABS": {
        "label": "Asset-Backed Securities",
        "dataset": "assetBackedSecurities",
        "fields": [
            "finraSecurityIdentifier",
            "cusip",
            "issueSymbolIdentifier",
            "issuerName",
            "issueDescription",
            "dealId",
            "trancheId",
            "productSubTypeCode",
            "subProductType",
            "interestType",
            "couponRate",
            "couponType",
            "maturityDate",
            "is144A",
            "moodysRating",
            "moodysRatingDate",
            "lastSalePrice",
            "lastTradeDate",
            "priceChangeNumber",
            "priceChangePercent",
        ],
    },
    "CMO": {
        "label": "Collateralized Mortgage Obligations",
        "dataset": "collateralizedMortgageObligationsSecurities",
        "fields": [
            "finraSecurityIdentifier",
            "cusip",
            "issueSymbolIdentifier",
            "issuerName",
            "issuingAgency",
            "securityDescription",
            "productType",
            "productSubTypeCode",
            "subProductType",
            "couponRate",
            "couponType",
            "maturityDate",
            "is144A",
            "moodysRating",
            "lastSalePrice",
            "lastTradeDate",
            "priceChangeNumber",
            "priceChangePercent",
        ],
    },
}

UNFILTERED_BOND_TYPES = ("CA", "TS", "TBA", "ABS")

BOND_SEARCH_DATASET = "bondSearch"
BOND_SEARCH_FIELDS = ["cusip", "issueSymbolIdentifier", "issuerName", "bondType"]

HISTORY_DATASETS: dict[str, dict] = {
    "TS": {
        "dataset": "treasuryEndOfDayPriceYield",
        "fields": [
            "tradeDate",
            "finraSecurityIdentifier",
            "cusip",
            "issueSymbolIdentifier",
            "lastSalePrice",
            "lastSaleYield",
            "dailyLastSaleYieldDirection",
        ],
    },
    "OTHER": {
        "dataset": "endOfDayPriceYield",
        "fields": [
            "tradeDate",
            "finraSecurityIdentifier",
            "cusip",
            "issueSymbolIdentifier",
            "productType",
            "lastSalePrice",
            "lastSaleYield",
        ],
    },
}
HISTORY_DAYS = 1825

TRACE_NUMBER_FIELDS = {
    "averageLoanSize",
    "couponRate",
    "lastSalePrice",
    "lastSaleYield",
    "loanToValueRatio",
    "originalMaturityTerm",
    "priceChangeNumber",
    "priceChangePercent",
    "weightedAverageCoupon",
    "weightedAverageLoanAge",
    "weightedAverageMaturity",
}
TRACE_BOOL_FIELDS = {"isCallable", "isConvertible", "is144A", "isPerpetual"}
TRACE_DATE_FIELDS = {
    "lastTradeDate",
    "maturityDate",
    "moodyRatingDate",
    "moodysRatingDate",
    "nextCallDate",
    "standardAndPoorsRatingDate",
    "tradeDate",
}

CORPORATE_COUPON_TYPES = {
    "CNGT": "Contingent",
    "FRBF": "Bull/Reverse Floating",
    "FRFF": "Fixed then Floating",
    "FRFX": "Floating then Fixed",
    "FRFZ": "Floating then Zero",
    "FROT": "Floating",
    "FRPM": "Floating Pay at Maturity",
    "FRPV": "Fixed Margin over Index",
    "FRRS": "Floating then Reset",
    "FRSD": "Step-Down Margin over Index",
    "FRSU": "Step-Up Margin over Index",
    "FRVR": "Floating then Variable",
    "FRZF": "Zero then Floating",
    "FTZR": "Fixed then Zero",
    "FXAN": "Fixed Annuity",
    "FXDI": "Fixed Discount",
    "FXMF": "Fixed Multiple Payment Frequencies",
    "FXPM": "Fixed Pay only at Maturity",
    "FXPP": "Fixed Partly Paid",
    "FXPV": "Fixed Plain Vanilla",
    "FXRS": "Resettable",
    "FXRV": "Fixed then Reverse Float",
    "FXZC": "Fixed Zero Coupon",
    "RGOT": "Range",
    "RSFR": "Reset then Floating",
    "STRP": "Strip",
    "TBPD": "To Be Priced",
    "VRDC": "Variable Deferred Coupon",
    "VRFR": "Variable then Floating",
    "VRGR": "Step Up/Step Down",
    "ZCFX": "Zero then Fixed",
    "ZRFX": "Zero then Fixed",
    "ZRVR": "Zero then Variable",
}

STRUCTURED_COUPON_TYPES = {
    "ARB": "Ascending Rate",
    "CFLT": "Complex Floater",
    "DRB": "Descending Rate",
    "FIX": "Fixed",
    "FLT": "Floater",
    "FLTFX": "Floater to Fixed",
    "FLTVAR": "Floater to Variable",
    "FLTWAC": "Floater to WAC",
    "FRRS": "Flt then Reset",
    "FXFL": "Fixed to Floater",
    "FXRS": "Resettable",
    "FXVAR": "Fixed to Variable",
    "FXWAC": "Fixed to WAC",
    "INV": "Inverse Floating Rate",
    "RSFR": "Reset then Flt",
    "STRFLT": "Structured Floater",
    "STRINV": "Structured Inverse Floater",
    "TFLT": "Toggle Floater",
    "TINV": "Toggle Inverse",
    "VAR": "Variable",
    "WGTSUB": "Weighted Average of Subordinate",
}

TBA_COUPON_TYPES = {
    "A": "ARM",
    "B": "Balloon",
    "W": "Biweekly",
    "H": "GEM",
    "G": "GPM",
    "L": "Level Pay",
    "T": "TPM",
    "R": "Fixed Rate Reverse",
}

COUPON_TYPES: dict[str, dict[str, str]] = {
    "CA": CORPORATE_COUPON_TYPES,
    "TS": STRUCTURED_COUPON_TYPES,
    "ABS": STRUCTURED_COUPON_TYPES,
    "CMO": STRUCTURED_COUPON_TYPES,
    "TBA": TBA_COUPON_TYPES,
    "MBS": TBA_COUPON_TYPES,
}

INDUSTRY_GROUPS = {
    "AERO": "Aerospace",
    "AGENCY": "Agency",
    "AGNC": "Agency",
    "AIRL": "Airline",
    "AUTO": "Automotive Manufacturer",
    "BANK": "Banking",
    "BANKS": "Banks",
    "BEVG": "Beverage/Bottling",
    "BLDG": "Building Products",
    "CABL": "Cable/Media",
    "CHEM": "Chemicals",
    "CONG": "Conglomerate/Diversified Mfg",
    "CONS": "Consumer Products",
    "CONSUMGD": "Consumer Goods",
    "ELECTRIC": "Electric Power",
    "ENERGY": "Energy Company",
    "FDRG": "Retail Stores - Food/Drug",
    "FOOD": "Food Processors",
    "FUNN": "Leisure",
    "GAME": "Gaming",
    "GASDISTR": "Gas Distribution",
    "GASL": "Gas Utility - Local Distrib",
    "GASP": "Gas Utility - Pipelines",
    "HEAL": "Health Care Supply",
    "HLCF": "Health Care Facilities",
    "HOME": "Home Builders",
    "INDFINCL": "Independent Finance",
    "INFO": "Information/Data Technology",
    "LEAS": "Leasing",
    "LIFE": "Life Insurance",
    "LODG": "Lodging",
    "MACH": "Machinery",
    "MANUFACT": "Manufacturing",
    "METL": "Metals/Mining",
    "MTGB": "Mortgage Banking",
    "OFFMUNI": "Official and Muni",
    "OILG": "Oil and Gas",
    "OILM": "Oilfield Machinery and Services",
    "OTHF": "Financial - Other",
    "OTHFINCL": "Other Financial",
    "OTHI": "Industrials - Other",
    "OTHS": "Service - Other",
    "OTHT": "Transportation - Other",
    "OTHU": "Utility - Other",
    "PACK": "Containers",
    "PCAS": "Property and Casualty Insurance",
    "PHRM": "Pharmaceuticals",
    "PUBL": "Publishing",
    "RAIL": "Railroads",
    "REIT": "Real Estate Investment Trust",
    "REST": "Restaurants",
    "RETL": "Retail Stores - Other",
    "SECS": "Securities",
    "SERVICE": "Service Company",
    "SOVERGRN": "Sovereign",
    "SPRA": "Supranational",
    "SVSG": "Sovereign",
    "TELE": "Telecommunications",
    "TELEPHON": "Telephone",
    "TEXT": "Textiles/Apparel/Shoes",
    "TOBC": "Tobacco",
    "TRANSPRT": "Transportation",
    "TRON": "Electronics",
    "VEHL": "Vehicle Parts",
}

TRACE_GRADES = {"H": "High Yield", "I": "Investment Grade"}

OTC_TIERS = Literal["T1", "T2", "OTCE"]

PRODUCT_SUB_TYPES = {
    "AGCY": "Agency Bond",
    "CHRC": "Church Bond",
    "CORP": "Corporate Bond",
    "ELN": "Equity Linked Note",
    "NOTE": "Notes, Bonds",
    "TBA": "To-Be-Announced",
    "MBS": "Mortgage-Backed Security",
    "ABS": "Asset-Backed Security",
    "ABSX": "Asset-Backed Security (144A)",
    "CMO": "Collateralized Mortgage Obligation",
}

SUB_PRODUCT_TYPES = {
    "POOL": "Agency Pass-through Securities",
    "GNM1": "Ginnie Mae 1",
    "GNM2": "Ginnie Mae 2",
    "GD": "For Good Delivery",
    "NGD": "Not For Good Delivery",
    "AGRI": "CMO Agricultural MBS",
    "TRAN": "CMO Tranches",
    "WHLN": "CMO Whole Loan",
    "HLOC": "Home Equity Lines of Credit",
    "HOME": "Home Equity Loans",
    "AGNM": "Net Interest Margin",
    "CRSK": "CMO Credit Risk Sharing",
    "HREM": "Home Equity Conversion Mortgage REMIC",
    "CMBS": "Commercial Mortgage-Backed Security",
    "ALEA": "Auto Lease Loans",
    "AFLP": "Auto Floor Plan/Wholesale Loans",
    "AUTO": "Auto Installment Loans",
    "RECR": "Recreational Vehicle Loans",
    "BIKE": "Motorcycle Lease",
    "SBA": "Small Business Administration",
    "CARD": "Credit Card Receivables",
    "STUD": "Student Loan",
    "MANU": "Manufactured Housing Loan",
    "AIRL": "Aircraft Lease",
    "BOAT": "Marine Loans",
    "BUSL": "ABS Business Loans",
    "CNSL": "Consumer Loans",
    "CONT": "ABS Container Backed Securities",
    "DPR": "Diversified Payment Rights",
    "TXLN": "Tax Lien",
    "EQIP": "Equipment Backed Loan",
    "EXIM": "Export/Import Bank Loan",
    "NIM": "Net Interest Margin Securities",
    "OTHR": "Asset Backed Tranches",
    "RVMG": "Reverse Mortgage",
    "UTIL": "Utility Standard Cost Securitizations",
    "CTSR": "Catastrophe ABS",
    "LOTT": "Lottery Ticket ABS",
    "PNSN": "Pension Securitization",
    "PSNL": "Personal Loan ABS",
    "RENT": "Rent ABS",
    "RINS": "Reinsurance ABS",
    "TMSH": "Timeshare ABS",
    "MHSG": "Military Housing",
    "CBO": "Collateralized Bond Obligation",
    "CDO": "Collateralized Debt Obligation",
    "CFO": "Collateralized Fund Obligation",
    "CLO": "Collateralized Loan Obligation",
}

INTEREST_TYPES = {
    "IOET": "Ioette",
    "IONTL": "Interest Only Notional",
    "PNTL": "Partial Notional",
    "PO": "Principal Only",
    "POHYB": "Hybrid Principal Only",
    "STPCLL": "Step-Up on Call",
    "STPCLWAC": "Step-Up on Call Subject to WACCAP",
    "STPDT": "Step-Up on Date",
    "STPDTWAC": "Step-Up on Date Subject to WACCAP",
    "STPRLY": "Step-Up on Earliest Call or Date",
    "STPRYWAC": "Step-Up on Earliest Call or Date, Subject to WACCAP",
    "WACCAP": "WAC Cap",
}

MORTGAGE_PRODUCTS = {
    "A": "Affordable Housing",
    "B": "Planned Urban Development (PUD)",
    "C": "Co-op",
    "D": "Project",
    "H": "Home Improvement Loans",
    "L": "Leasehold",
    "M": "Multi-Family",
    "N": "Condominium",
    "P": "Manufactured/Prefab",
    "R": "Senior",
    "S": "Single Family",
    "T": "Student",
    "U": "Unknown",
    "Y": "Military",
    "#": "SBA; Unknown",
}

AMORTIZATION_TYPES = {
    "A": "ARM",
    "B": "Balloon",
    "D": "Discount",
    "G": "GPM - Graduated Payment Mortgage",
    "H": "GEM - Growing Equity Mortgage",
    "L": "Level Pay",
    "R": "Fixed Rate Reverse",
    "T": "TPM - Tiered Payment Mortgage",
    "V": "ARM Reverse",
    "W": "Biweekly",
    "Y": "Buydown",
}

MONTHS = {
    "1": "January",
    "2": "February",
    "3": "March",
    "4": "April",
    "5": "May",
    "6": "June",
    "7": "July",
    "8": "August",
    "9": "September",
    "10": "October",
    "11": "November",
    "12": "December",
}

PRICE_TYPES = {"D": "Decimal", "Y": "Yield", "N": "Negative Yield"}

PRODUCT_TYPES = {
    "CA": "Corporate and Agency",
    "SP": "Securitized Products",
    "TS": "U.S. Treasury",
}

SECURITY_TYPES = {
    "ST": "Stock",
    "FE": "ETF",
    "FC": "Closed-End Fund",
    "FO": "Open-End Fund",
    "XI": "Index",
}

EQUITY_PRODUCT_TYPES = {
    "UTP": "Nasdaq-Listed (UTP Plan)",
    "CTS": "NYSE and Regional Exchange-Listed (CTA Plan)",
    "OTCE": "OTC Equity",
}

MARKET_CLASSES = {
    "NNM": "Nasdaq Global Select and Global Market",
    "SC": "Nasdaq Capital Market",
    "NYSE": "New York Stock Exchange",
    "AMEX": "NYSE American",
    "ARCA": "NYSE Arca",
    "BZX": "Cboe BZX",
    "OTC": "OTC",
}
