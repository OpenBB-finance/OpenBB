"""BLS Provider Constants."""

from typing import Literal

PPI_SURVEYS = ["WP", "PC"]
PCE_SURVEYS = ["CX"]
CPI_SURVEYS = ["AP", "CU", "CW", "LI", "SU", "EI"]
PRODUCTIVITY_SURVEYS = ["IP", "PR", "MP"]
LABOR_FORCE_STATISTICS = ["LN", "FM", "IN", "WS"]
CURRENT_POPULATION_SURVEY = ["LE", "LU"]
LOCAL_EMPLOYMENT_SURVEYS = ["LA", "SM"]
JOLTS_SURVEYS = ["JL", "JT"]
NFP_SURVEYS = ["CE"]
WAGES_SURVEYS = ["CI", "WM"]
EMPLOYER_COSTS = ["CM", "CC"]
BUSINESS_EMPLOYMENT_DYNAMICS = ["BD"]
TIME_USE_SURVEYS = ["TU"]

SUPPORTED_SURVEYS = sorted(
    list(
        PPI_SURVEYS
        + PCE_SURVEYS
        + CPI_SURVEYS
        + PRODUCTIVITY_SURVEYS
        + LABOR_FORCE_STATISTICS
        + LOCAL_EMPLOYMENT_SURVEYS
        + CURRENT_POPULATION_SURVEY
        + JOLTS_SURVEYS
        + NFP_SURVEYS
        + WAGES_SURVEYS
        + EMPLOYER_COSTS
        + BUSINESS_EMPLOYMENT_DYNAMICS
        + TIME_USE_SURVEYS
    )
)

SURVEY_CATEGORY_MAP = {
    "cpi": [d.lower() for d in CPI_SURVEYS],
    "pce": [d.lower() for d in PCE_SURVEYS],
    "ppi": [d.lower() for d in PPI_SURVEYS],
    "ip": [d.lower() for d in PRODUCTIVITY_SURVEYS],
    "jolts": [d.lower() for d in JOLTS_SURVEYS],
    "nfp": [d.lower() for d in NFP_SURVEYS],
    "cps": [d.lower() for d in CURRENT_POPULATION_SURVEY],
    "lfs": [d.lower() for d in LABOR_FORCE_STATISTICS],
    "wages": [d.lower() for d in WAGES_SURVEYS],
    "ec": [d.lower() for d in EMPLOYER_COSTS],
    "sla": [d.lower() for d in LOCAL_EMPLOYMENT_SURVEYS],
    "bed": [d.lower() for d in BUSINESS_EMPLOYMENT_DYNAMICS],
    "tu": [d.lower() for d in TIME_USE_SURVEYS],
}

SURVEY_CATEGORY_NAMES = {
    "cpi": "Consumer Price Index",
    "pce": "Personal Consumption Expenditure",
    "ppi": "Producer Price Index",
    "ip": "Industry Productivity",
    "jolts": "Job Openings and Labor Turnover Survey",
    "nfp": "Nonfarm Payrolls",
    "cps": "Current Population Survey",
    "lfs": "Labor Force Statistics",
    "wages": "Wages",
    "ec": "Employer Costs",
    "sla": "State and Local Area Employment",
    "bed": "Business Employment Dynamics",
    "tu": "Time Use",
}

SURVEY_CATEGORIES = Literal[
    "cpi",
    "pce",
    "ppi",
    "ip",
    "jolts",
    "nfp",
    "cps",
    "lfs",
    "wages",
    "ec",
    "sla",
    "bed",
    "tu",
]

ALL_SURVEYS = [
    {
        "survey_name": "Consumer Price Index - Average Price Data",
        "survey_abbreviation": "AP",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Business Employment Dynamics",
        "survey_abbreviation": "BD",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Collective Bargaining Agreements-State and Local Government",
        "survey_abbreviation": "BG",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Collective Bargaining Agreements-Private Sector",
        "survey_abbreviation": "BP",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Biennial Nonfatal Case and Demographic numbers and rates: selected characteristics",
        "survey_abbreviation": "CB",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Employer Costs for Employee Compensation",
        "survey_abbreviation": "CC",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Nonfatal cases involving days away from work: selected characteristics",
        "survey_abbreviation": "CD",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Employment, Hours, and Earnings from the Current Employment Statistics survey (National)",
        "survey_abbreviation": "CE",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Census of Fatal Occupational Injuries",
        "survey_abbreviation": "CF",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Nonfatal cases involving days away from work: selected characteristics (2003 - 2010)",
        "survey_abbreviation": "CH",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Employment Cost Index",
        "survey_abbreviation": "CI",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Employer Costs for Employee Compensation",
        "survey_abbreviation": "CM",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Nonfatal cases involving days away from work: selected characteristics (2011 forward)",
        "survey_abbreviation": "CS",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Consumer Price Index - All Urban Consumers",
        "survey_abbreviation": "CU",
        "allowsNetChange": "false",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Consumer Price Index - Urban Wage Earners and Clerical Workers",
        "survey_abbreviation": "CW",
        "allowsNetChange": "false",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Consumer Expenditure Survey",
        "survey_abbreviation": "CX",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Import/Export Price Indexes",
        "survey_abbreviation": "EI",
        "allowsNetChange": "false",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Quarterly Census of Employment and Wages (SIC)",
        "survey_abbreviation": "EW",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Census of Fatal Occupational Injuries (2003 - 2010)",
        "survey_abbreviation": "FI",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Marital and family labor force statistics from the Current Population Survey",
        "survey_abbreviation": "FM",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Census of Fatal Occupational Injuries (2011 forward)",
        "survey_abbreviation": "FW",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Nonfatal cases involving days away from work: Selected Characteristics (2002)",
        "survey_abbreviation": "HC",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Occupational injuries and illnesses: industry data (pre-1989)",
        "survey_abbreviation": "HS",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Occupational injuries and illnesses: industry data",
        "survey_abbreviation": "II",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "International Labor Comparison",
        "survey_abbreviation": "IN",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Industry Productivity",
        "survey_abbreviation": "IP",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Occupational injuries and illnesses industry data",
        "survey_abbreviation": "IS",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Job Openings and Labor Turnover Survey",
        "survey_abbreviation": "JL",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Job Openings and Labor Turnover Survey",
        "survey_abbreviation": "JT",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Local Area Unemployment Statistics",
        "survey_abbreviation": "LA",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Weekly and hourly earnings data from the Current Population Survey",
        "survey_abbreviation": "LE",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Consumer Price Index - Department Store Inventory Price Index",
        "survey_abbreviation": "LI",
        "allowsNetChange": "false",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Labor Force Statistics from the Current Population Survey",
        "survey_abbreviation": "LN",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Union affiliation data from the Current Population Survey",
        "survey_abbreviation": "LU",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Major Sector Total Factor Productivity",
        "survey_abbreviation": "MP",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "National Compensation Survey-Benefits",
        "survey_abbreviation": "NB",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "National Compensation Survey",
        "survey_abbreviation": "NC",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "National Compensation Survey",
        "survey_abbreviation": "NW",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Occupational Employment and Wage Statistics",
        "survey_abbreviation": "OE",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Occupational Requirements",
        "survey_abbreviation": "OR",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Producer Price Index Industry Data",
        "survey_abbreviation": "PC",
        "allowsNetChange": "false",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Major Sector Productivity and Costs",
        "survey_abbreviation": "PR",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Occupational injuries and illnesses: industry data (1989-2001)",
        "survey_abbreviation": "SH",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Occupational injuries and illnesses: industry data (2002)",
        "survey_abbreviation": "SI",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "State and Area Employment, Hours, and Earnings",
        "survey_abbreviation": "SM",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Consumer Price Index - Chained Consumer Price Index",
        "survey_abbreviation": "SU",
        "allowsNetChange": "false",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "American Time Use",
        "survey_abbreviation": "TU",
        "allowsNetChange": "false",
        "allowsPercentChange": "false",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Wage Modeling",
        "survey_abbreviation": "WM",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "false",
    },
    {
        "survey_name": "Producer Price Index-Commodities",
        "survey_abbreviation": "WP",
        "allowsNetChange": "false",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
    {
        "survey_name": "Work Stoppage Data",
        "survey_abbreviation": "WS",
        "allowsNetChange": "true",
        "allowsPercentChange": "true",
        "hasAnnualAverages": "true",
    },
]

SURVEY_NAMES = {
    d["survey_abbreviation"].lower(): d["survey_name"]
    for d in ALL_SURVEYS
    if d["survey_abbreviation"] in SUPPORTED_SURVEYS
}
