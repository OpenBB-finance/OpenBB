"""RSS feed registry."""

from urllib.parse import quote

from openbb_core.app.config.loader import load_config

_PROVIDER_LABELS: dict[str, str] = {
    "axios": "Axios",
    "bbc": "BBC",
    "benzinga": "Benzinga",
    "cbc": "CBC",
    "drudge_report": "Drudge Report",
    "fox_news": "Fox News",
    "fortune": "Fortune",
    "globenewswire": "GlobeNewswire",
    "google_news": "Google News",
    "yahoo_finance": "Yahoo Finance",
    "pr_newswire": "PR Newswire",
    "wired": "Wired",
    "custom": "Custom",
}

_PRNEWSWIRE_REGIONS: tuple[str, ...] = (
    "apac",
    "apac/zh",
    "br",
    "jp",
    "kr",
    "mx",
    "id",
    "vn",
)
_PRNEWSWIRE_REGION_LABELS: dict[str, str] = {
    "global": "Global",
    "apac": "APAC",
    "apac/zh": "APAC (Chinese)",
    "br": "Brazil",
    "jp": "Japan",
    "kr": "Korea",
    "mx": "Mexico",
    "id": "Indonesia",
    "vn": "Vietnam",
}
_PRNEWSWIRE_CATEGORIES: tuple[str, ...] = (
    "business-technology",
    "consumer-products-retail",
    "consumer-technology",
    "energy",
    "entertainment-media",
    "environment",
    "general-business",
    "heavy-industry-manufacturing",
    "health",
    "people-culture",
    "policy-public-interest",
    "sports",
    "telecommunications",
    "travel",
    "financial-services",
    "automotive-transportation",
)
_PRNEWSWIRE_CATEGORY_LABELS: dict[str, str] = {
    "business-technology": "Business Technology",
    "consumer-products-retail": "Consumer Products & Retail",
    "consumer-technology": "Consumer Technology",
    "energy": "Energy",
    "entertainment-media": "Entertainment & Media",
    "environment": "Environment",
    "general-business": "General Business",
    "heavy-industry-manufacturing": "Heavy Industry & Manufacturing",
    "health": "Health",
    "people-culture": "People & Culture",
    "policy-public-interest": "Policy & Public Interest",
    "sports": "Sports",
    "telecommunications": "Telecommunications",
    "travel": "Travel",
    "financial-services": "Financial Services",
    "automotive-transportation": "Automotive & Transportation",
}
_PRNEWSWIRE_GLOBAL_SKIP: frozenset[str] = frozenset({"business-technology"})

_GLOBENEWSWIRE_INDUSTRIES: tuple[tuple[str, str], ...] = (
    ("2713", "Aerospace"),
    ("5751", "Airlines"),
    ("7537", "Alternative Electricity"),
    ("587", "Alternative Fuels"),
    ("1753", "Aluminum"),
    ("5371", "Apparel Retailers"),
    ("8771", "Asset Managers and Custodians"),
    ("3355", "Auto Parts"),
    ("40101010", "Auto Services"),
    ("3353", "Automobiles"),
    ("8355", "Banks"),
    ("1000", "Basic Materials"),
    ("4573", "Biotechnology"),
    ("3533", "Brewers"),
    ("5553", "Broadcasting and Entertainment"),
    ("5373", "Broadline Retailers"),
    ("50101025", "Building Climate Control"),
    ("2353", "Building Materials and Fixtures"),
    ("50101035", "Building Materials Other"),
    ("50101020", "Building, Roofing, Wallboard and Plumbing"),
    ("2791", "Business Support Services"),
    ("2793", "Business Training and Employment Agencies"),
    ("20103020", "Cannabis Producers"),
    ("50101030", "Cement"),
    ("55201010", "Chemicals and Synthetic Fibers"),
    ("55201000", "Chemicals Diversified"),
    ("30204000", "Closed End Investments"),
    ("3763", "Clothing and Accessories"),
    ("1771", "Coal"),
    ("50206050", "Commercial Vehicle Equipment Leasing"),
    ("50206015", "Commercial Vehicles and Parts"),
    ("2753", "Commercial Vehicles and Trucks"),
    ("1353", "Commodity Chemicals"),
    ("9572", "Computer Hardware"),
    ("9533", "Computer Services"),
    ("50101010", "Construction"),
    ("3743", "Consumer Electronics"),
    ("8773", "Consumer Finance"),
    ("3000", "Consumer Goods"),
    ("5000", "Consumer Services"),
    ("2723", "Containers and Packaging"),
    ("7535", "Conventional Electricity"),
    ("55102040", "Copper"),
    ("2717", "Defense"),
    ("2771", "Delivery Services"),
    ("1773", "Diamonds and Gemstones"),
    ("3535", "Distillers and Vintners"),
    ("30202000", "Diversified Financial Services"),
    ("2727", "Diversified Industrials"),
    ("55101000", "Diversified Materials"),
    ("8674", "Diversified REITs"),
    ("5333", "Drug Retailers"),
    ("3722", "Durable Household Products"),
    ("50202010", "Electrical Components"),
    ("2733", "Electrical Components and Equipment"),
    ("2737", "Electronic Equipment"),
    ("50202020", "Electronic Equipment Control and Filter"),
    ("50202025", "Electronic Equipment Gauges and Meters"),
    ("50202040", "Electronic Equipment Other"),
    ("50202030", "Electronic Equipment Pollution Control"),
    ("9574", "Electronic Office Equipment"),
    ("1", "Energy"),
    ("50101015", "Engineering and Contracting Services"),
    ("8985", "Equity Investment Instruments"),
    ("533", "Exploration and Production"),
    ("3573", "Farming and Fishing"),
    ("55201015", "Fertilizers"),
    ("2795", "Financial Administration"),
    ("30201030", "Financial Data Providers"),
    ("8000", "Financials"),
    ("6535", "Fixed Line Telecommunications"),
    ("3577", "Food Products"),
    ("5337", "Food Retailers and Wholesalers"),
    ("3765", "Footwear"),
    ("1733", "Forestry"),
    ("50205030", "Forms and Bulk Printing Services"),
    ("8532", "Full Line Insurance"),
    ("3726", "Furnishings"),
    ("5752", "Gambling"),
    ("7573", "Gas Distribution"),
    ("1775", "General Mining"),
    ("50203020", "Glass"),
    ("1777", "Gold Mining"),
    ("4000", "Health Care"),
    ("4533", "Health Care Providers"),
    ("35102010", "Health Care REITs"),
    ("2357", "Heavy Construction"),
    ("3728", "Home Construction"),
    ("5375", "Home Improvement Retailers"),
    ("8677", "Hotel and Lodging REITs"),
    ("5753", "Hotels"),
    ("8671", "Industrial and Office REITs"),
    ("2757", "Industrial Machinery"),
    ("35102020", "Industrial REITs"),
    ("2797", "Industrial Suppliers"),
    ("2000", "Industrials"),
    ("35102025", "Infrastructure REITs"),
    ("8534", "Insurance Brokers"),
    ("537", "Integrated Oil and Gas"),
    ("9535", "Internet"),
    ("8777", "Investment Services"),
    ("1757", "Iron and Steel"),
    ("8575", "Life Insurance"),
    ("50204010", "Machinery Agricultural"),
    ("50204020", "Machinery Construction and Handling"),
    ("50204030", "Machinery Engines"),
    ("50204000", "Machinery Industrial"),
    ("50204050", "Machinery Specialty"),
    ("50204040", "Machinery Tools"),
    ("2773", "Marine Transportation"),
    ("5555", "Media Agencies"),
    ("4535", "Medical Equipment"),
    ("20102020", "Medical Services"),
    ("4537", "Medical Supplies"),
    ("55102015", "Metal Fabricating"),
    ("6575", "Mobile Telecommunications"),
    ("8779", "Mortgage Finance"),
    ("8676", "Mortgage REITs"),
    ("7575", "Multiutilities"),
    ("3724", "Nondurable Household Products"),
    ("8995", "Nonequity Investment Instruments"),
    ("1755", "Nonferrous Metals"),
    ("35102030", "Office REITs"),
    ("573", "Oil Equipment and Services"),
    ("30205000", "Open End and Miscellaneous Investment Vehicles"),
    ("35102070", "Other Specialty REITs"),
    ("50203010", "Paints and Coatings"),
    ("1737", "Paper"),
    ("3767", "Personal Products"),
    ("4577", "Pharmaceuticals"),
    ("577", "Pipelines"),
    ("50203015", "Plastics"),
    ("1779", "Platinum and Precious Metals"),
    ("10102020", "Production Technology Equipment"),
    ("50205020", "Professional Business Support Services"),
    ("8536", "Property and Casualty Insurance"),
    ("5557", "Publishing"),
    ("50206025", "Railroad Equipment"),
    ("2775", "Railroads"),
    ("35", "Real Estate"),
    ("8633", "Real Estate Holding and Development"),
    ("8637", "Real Estate Services"),
    ("3745", "Recreational Products"),
    ("5755", "Recreational Services"),
    ("8538", "Reinsurance"),
    ("583", "Renewable Energy Equipment"),
    ("8673", "Residential REITs"),
    ("5757", "Restaurants and Bars"),
    ("8672", "Retail REITs"),
    ("50205040", "Security Services"),
    ("9576", "Semiconductors"),
    ("3537", "Soft Drinks"),
    ("9537", "Software"),
    ("5377", "Specialized Consumer Services"),
    ("1357", "Specialty Chemicals"),
    ("8775", "Specialty Finance"),
    ("8675", "Specialty REITs"),
    ("5379", "Specialty Retailers"),
    ("35102050", "Storage REITs"),
    ("9000", "Technology"),
    ("6000", "Telecommunications"),
    ("9578", "Telecommunications Equipment"),
    ("55101020", "Textile Products"),
    ("35102060", "Timber REITs"),
    ("3357", "Tires"),
    ("3785", "Tobacco"),
    ("3747", "Toys"),
    ("50205015", "Transaction Processing Services"),
    ("2777", "Transportation Services"),
    ("5759", "Travel and Tourism"),
    ("2779", "Trucking"),
    ("7000", "Utilities"),
    ("2799", "Waste and Disposal Services"),
    ("7577", "Water"),
)


def _globenewswire_industry_url(code: str, label: str) -> str:
    """Build a GlobeNewswire industry feed URL."""
    title = quote(f"GlobeNewswire - Industry News on {label}", safe="-")
    return f"https://www.globenewswire.com/AtomFeed/industry/{code}/feedTitle/{title}"


def _globenewswire_industry_key(label: str) -> str:
    """Slug an industry label into a feed key."""
    return _globenewswire_slug(label, prefix="globenewswire_")


_GLOBENEWSWIRE_SUBJECTS: tuple[tuple[str, str], ...] = (
    ("1", "Advisory"),
    ("3", "Analyst Recommendations"),
    ("2", "Annual Meetings and Shareholder Rights"),
    ("65", "Annual Report"),
    ("4", "Arts and Entertainment"),
    ("5", "Bankruptcy"),
    ("6", "Bond Market News"),
    ("74", "Bonds Market Information"),
    ("7", "Business Contracts"),
    ("8", "Calendar Of Events"),
    ("58", "Changes In Company's Own Shares"),
    ("57", "Changes In Share Capital And Votes"),
    ("71", "Changes To Observation Segment"),
    ("84", "Class Action"),
    ("90", "Clinical Study"),
    ("9", "Company Announcement"),
    ("10", "Company Regulatory Filings"),
    ("89", "Conference Calls, Webcasts"),
    ("88", "Contests, Awards"),
    ("61", "Corporate Action"),
    ("75", "Derivative Market Information"),
    ("11", "Directors And Officers"),
    ("12", "Dividend Reports and Estimates"),
    ("13", "Earnings Releases and Operating Results"),
    ("14", "Economic Research And Reports"),
    ("91", "Environmental, Social, And Governance Criteria"),
    ("76", "Equity Market Information"),
    ("85", "European Regulatory News"),
    ("70", "Exchange Announcement"),
    ("77", "Exchange Members"),
    ("78", "Exchange News"),
    ("15", "Fashion"),
    ("16", "Feature Article"),
    ("17", "Financing Agreements"),
    ("69", "First North Announcement"),
    ("79", "First North Information"),
    ("18", "Food"),
    ("19", "Government News"),
    ("20", "Health"),
    ("21", "Initial Public Offerings"),
    ("22", "Insider's Buy, Sell"),
    ("66", "Interim Information"),
    ("80", "Investment Fund Information"),
    ("83", "Investment Opinion"),
    ("23", "Joint Venture"),
    ("24", "Law and Legal Issues"),
    ("25", "Licensing Agreements"),
    ("26", "Lifestyle"),
    ("59", "Major Shareholder Announcements"),
    ("86", "Management Changes"),
    ("67", "Management Statements"),
    ("81", "Market Research Reports"),
    ("27", "Mergers and Acquisitions"),
    ("64", "Mutual Fund Information"),
    ("62", "Net Asset Value"),
    ("28", "Other News"),
    ("29", "Partnerships"),
    ("30", "Patents"),
    ("87", "Philanthropy"),
    ("34", "Politics"),
    ("31", "Pre Release Comments"),
    ("72", "Press Releases"),
    ("32", "Product, Services Announcement"),
    ("63", "Prospectus, Announcement Of Prospectus"),
    ("33", "Proxy Statements And Analysis"),
    ("73", "Regulatory Information"),
    ("35", "Religion"),
    ("36", "Research Analysis And Reports"),
    ("37", "Restructuring, Recapitalization"),
    ("38", "Sports"),
    ("39", "Stock Market News"),
    ("40", "Tax Issues, Accounting"),
    ("43", "Technical Analysis"),
    ("41", "Trade Show"),
    ("68", "Trading Information"),
    ("42", "Travel"),
    ("82", "Warrants And Certificates"),
)


def _globenewswire_subject_url(code: str, label: str) -> str:
    """Build a GlobeNewswire subject feed URL."""
    title = quote(f"GlobeNewswire - {label}", safe="-")
    return (
        f"https://www.globenewswire.com/AtomFeed/subjectcode/{code}/feedTitle/{title}"
    )


def _globenewswire_subject_key(label: str) -> str:
    """Slug a subject label into a feed key."""
    return _globenewswire_slug(label, prefix="globenewswire_subject_")


def _globenewswire_slug(label: str, prefix: str) -> str:
    """Slug a label."""
    import re

    slug = label.lower().replace("&", "and").replace("/", "_").replace("'", "")
    slug = slug.replace(":", "").replace(",", "").replace(".", "")
    slug = re.sub(r"[^a-z0-9]+", "_", slug).strip("_")
    return f"{prefix}{slug}"


_CURATED_FEEDS: dict[str, tuple[str, str, str]] = {
    "axios_main": ("axios", "Latest", "https://api.axios.com/feed/"),
    "benzinga_main": ("benzinga", "Latest", "https://www.benzinga.com/feed"),
    "benzinga_markets": (
        "benzinga",
        "Markets",
        "https://www.benzinga.com/markets/feed",
    ),
    "benzinga_general": (
        "benzinga",
        "General News",
        "https://www.benzinga.com/general/feed",
    ),
    "benzinga_cryptocurrency": (
        "benzinga",
        "Cryptocurrency",
        "https://www.benzinga.com/topic/cryptocurrency/feed",
    ),
    "benzinga_government": (
        "benzinga",
        "Government",
        "https://www.benzinga.com/topic/government/feed",
    ),
    "globenewswire_all": (
        "globenewswire",
        "All News",
        "https://www.globenewswire.com/RssFeed/orgclass/1/feedTitle/GlobeNewswire-AllNews",
    ),
    "globenewswire_us": (
        "globenewswire",
        "United States",
        "https://www.globenewswire.com/AtomFeed/country/United%20States/feedTitle/GlobeNewswire%20-%20News%20from%20United%20States",
    ),
    "bbc_world": ("bbc", "World", "http://feeds.bbci.co.uk/news/world/rss.xml"),
    "bbc_uk": ("bbc", "UK", "http://feeds.bbci.co.uk/news/uk/rss.xml"),
    "bbc_business": (
        "bbc",
        "Business",
        "http://feeds.bbci.co.uk/news/business/rss.xml",
    ),
    "bbc_politics": (
        "bbc",
        "Politics",
        "http://feeds.bbci.co.uk/news/politics/rss.xml",
    ),
    "bbc_health": ("bbc", "Health", "http://feeds.bbci.co.uk/news/health/rss.xml"),
    "bbc_education": (
        "bbc",
        "Education",
        "http://feeds.bbci.co.uk/news/education/rss.xml",
    ),
    "bbc_science": (
        "bbc",
        "Science & Environment",
        "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    ),
    "bbc_technology": (
        "bbc",
        "Technology",
        "http://feeds.bbci.co.uk/news/technology/rss.xml",
    ),
    "bbc_entertainment": (
        "bbc",
        "Entertainment & Arts",
        "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    ),
    "cbc_world": ("cbc", "World", "https://www.cbc.ca/webfeed/rss/rss-world"),
    "cbc_canada": ("cbc", "Canada", "https://www.cbc.ca/webfeed/rss/rss-canada"),
    "cbc_business": (
        "cbc",
        "Business",
        "https://www.cbc.ca/webfeed/rss/rss-business",
    ),
    "cbc_politics": (
        "cbc",
        "Politics",
        "https://www.cbc.ca/webfeed/rss/rss-politics",
    ),
    "cbc_technology": (
        "cbc",
        "Technology",
        "https://www.cbc.ca/webfeed/rss/rss-technology",
    ),
    "cbc_health": ("cbc", "Health", "https://www.cbc.ca/webfeed/rss/rss-health"),
    "cbc_arts": ("cbc", "Arts", "https://www.cbc.ca/webfeed/rss/rss-arts"),
    "cbc_indigenous": (
        "cbc",
        "Indigenous",
        "https://www.cbc.ca/webfeed/rss/rss-Indigenous",
    ),
    "cbc_thenational": (
        "cbc",
        "The National",
        "https://www.cbc.ca/webfeed/rss/rss-thenational",
    ),
    "cbc_canada_britishcolumbia": (
        "cbc",
        "Region — British Columbia",
        "https://www.cbc.ca/webfeed/rss/rss-canada-britishcolumbia",
    ),
    "cbc_canada_calgary": (
        "cbc",
        "Region — Calgary",
        "https://www.cbc.ca/webfeed/rss/rss-canada-calgary",
    ),
    "cbc_canada_edmonton": (
        "cbc",
        "Region — Edmonton",
        "https://www.cbc.ca/webfeed/rss/rss-canada-edmonton",
    ),
    "cbc_canada_hamilton": (
        "cbc",
        "Region — Hamilton",
        "https://www.cbc.ca/webfeed/rss/rss-canada-hamiltonnews",
    ),
    "cbc_canada_kamloops": (
        "cbc",
        "Region — Kamloops",
        "https://www.cbc.ca/webfeed/rss/rss-canada-kamloops",
    ),
    "cbc_canada_kitchenerwaterloo": (
        "cbc",
        "Region — Kitchener-Waterloo",
        "https://www.cbc.ca/webfeed/rss/rss-canada-kitchenerwaterloo",
    ),
    "cbc_canada_london": (
        "cbc",
        "Region — London",
        "https://www.cbc.ca/webfeed/rss/rss-canada-london",
    ),
    "cbc_canada_manitoba": (
        "cbc",
        "Region — Manitoba",
        "https://www.cbc.ca/webfeed/rss/rss-canada-manitoba",
    ),
    "cbc_canada_montreal": (
        "cbc",
        "Region — Montreal",
        "https://www.cbc.ca/webfeed/rss/rss-canada-montreal",
    ),
    "cbc_canada_newbrunswick": (
        "cbc",
        "Region — New Brunswick",
        "https://www.cbc.ca/webfeed/rss/rss-canada-newbrunswick",
    ),
    "cbc_canada_newfoundland": (
        "cbc",
        "Region — Newfoundland",
        "https://www.cbc.ca/webfeed/rss/rss-canada-newfoundland",
    ),
    "cbc_canada_north": (
        "cbc",
        "Region — North",
        "https://www.cbc.ca/webfeed/rss/rss-canada-north",
    ),
    "cbc_canada_novascotia": (
        "cbc",
        "Region — Nova Scotia",
        "https://www.cbc.ca/webfeed/rss/rss-canada-novascotia",
    ),
    "cbc_canada_ottawa": (
        "cbc",
        "Region — Ottawa",
        "https://www.cbc.ca/webfeed/rss/rss-canada-ottawa",
    ),
    "cbc_canada_pei": (
        "cbc",
        "Region — Prince Edward Island",
        "https://www.cbc.ca/webfeed/rss/rss-canada-pei",
    ),
    "cbc_canada_saskatchewan": (
        "cbc",
        "Region — Saskatchewan",
        "https://www.cbc.ca/webfeed/rss/rss-canada-saskatchewan",
    ),
    "cbc_canada_saskatoon": (
        "cbc",
        "Region — Saskatoon",
        "https://www.cbc.ca/webfeed/rss/rss-canada-saskatoon",
    ),
    "cbc_canada_sudbury": (
        "cbc",
        "Region — Sudbury",
        "https://www.cbc.ca/webfeed/rss/rss-canada-sudbury",
    ),
    "cbc_canada_thunderbay": (
        "cbc",
        "Region — Thunder Bay",
        "https://www.cbc.ca/webfeed/rss/rss-canada-thunderbay",
    ),
    "cbc_canada_toronto": (
        "cbc",
        "Region — Toronto",
        "https://www.cbc.ca/webfeed/rss/rss-canada-toronto",
    ),
    "cbc_canada_windsor": (
        "cbc",
        "Region — Windsor",
        "https://www.cbc.ca/webfeed/rss/rss-canada-windsor",
    ),
    "cbc_sports_nhl": (
        "cbc",
        "Sports — NHL",
        "https://www.cbc.ca/webfeed/rss/rss-sports-nhl",
    ),
    "cbc_sports_nba": (
        "cbc",
        "Sports — NBA",
        "https://www.cbc.ca/webfeed/rss/rss-sports-nba",
    ),
    "cbc_sports_nfl": (
        "cbc",
        "Sports — NFL",
        "https://www.cbc.ca/webfeed/rss/rss-sports-nfl",
    ),
    "cbc_sports_mlb": (
        "cbc",
        "Sports — MLB",
        "https://www.cbc.ca/webfeed/rss/rss-sports-mlb",
    ),
    "cbc_sports_soccer": (
        "cbc",
        "Sports — Soccer",
        "https://www.cbc.ca/webfeed/rss/rss-sports-soccer",
    ),
    "fox_news_latest": (
        "fox_news",
        "Latest Headlines",
        "https://moxie.foxnews.com/google-publisher/latest.xml",
    ),
    "fox_news_world": (
        "fox_news",
        "World",
        "https://moxie.foxnews.com/google-publisher/world.xml",
    ),
    "fox_news_us": (
        "fox_news",
        "US",
        "https://moxie.foxnews.com/google-publisher/us.xml",
    ),
    "fox_news_politics": (
        "fox_news",
        "Politics",
        "https://moxie.foxnews.com/google-publisher/politics.xml",
    ),
    "google_news_us": (
        "google_news",
        "Top — US",
        "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    ),
    "google_news_ca": (
        "google_news",
        "Top — Canada",
        "https://news.google.com/rss?hl=en-CA&gl=CA&ceid=CA:en",
    ),
    "google_news_uk": (
        "google_news",
        "Top — UK",
        "https://news.google.com/rss?hl=en-GB&gl=GB&ceid=GB:en",
    ),
    "google_news_au": (
        "google_news",
        "Top — Australia",
        "https://news.google.com/rss?hl=en-AU&gl=AU&ceid=AU:en",
    ),
    "google_news_business": (
        "google_news",
        "Business",
        "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en",
    ),
    "google_news_technology": (
        "google_news",
        "Technology",
        "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
    ),
    "google_news_world": (
        "google_news",
        "World",
        "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en",
    ),
    "google_news_nation": (
        "google_news",
        "Nation",
        "https://news.google.com/rss/headlines/section/topic/NATION?hl=en-US&gl=US&ceid=US:en",
    ),
    "drudge_report": (
        "drudge_report",
        "Latest",
        "http://feeds.feedburner.com/DrudgeReportFeed",
    ),
    "fortune": (
        "fortune",
        "Latest",
        "https://fortune.com/feed/fortune-feeds/?id=3230629",
    ),
    "yahoo_finance": (
        "yahoo_finance",
        "Latest",
        "https://finance.yahoo.com/news/rssindex",
    ),
    "wired_main": ("wired", "Latest", "https://www.wired.com/feed/rss"),
    "wired_backchannel": (
        "wired",
        "Backchannel",
        "https://www.wired.com/feed/category/backchannel/latest/rss",
    ),
    "wired_business": (
        "wired",
        "Business",
        "https://www.wired.com/feed/category/business/latest/rss",
    ),
    "wired_culture": (
        "wired",
        "Culture",
        "https://www.wired.com/feed/category/culture/latest/rss",
    ),
    "wired_gear": (
        "wired",
        "Gear",
        "https://www.wired.com/feed/category/gear/latest/rss",
    ),
    "wired_ideas": (
        "wired",
        "Ideas",
        "https://www.wired.com/feed/category/ideas/latest/rss",
    ),
    "wired_science": (
        "wired",
        "Science",
        "https://www.wired.com/feed/category/science/latest/rss",
    ),
    "wired_security": (
        "wired",
        "Security",
        "https://www.wired.com/feed/category/security/latest/rss",
    ),
    "wired_ai": (
        "wired",
        "Tag — AI",
        "https://www.wired.com/feed/tag/ai/latest/rss",
    ),
    "wired_guide": (
        "wired",
        "Tag — Wired Guide",
        "https://www.wired.com/feed/tag/wired-guide/latest/rss",
    ),
}


def _slug(value: str) -> str:
    return value.replace("/", "_").replace("-", "_")


def _humanize(key: str) -> str:
    return key.replace("_", " ").title()


def _build_feed_registry() -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    feeds: dict[str, str] = {}
    meta: dict[str, dict[str, str]] = {}

    feeds["pr_newswire_global"] = (
        "https://www.prnewswire.com/rss/news-releases-list.rss"
    )
    meta["pr_newswire_global"] = {"provider": "pr_newswire", "label": "Global"}

    for region in _PRNEWSWIRE_REGIONS:
        key = f"pr_newswire_{_slug(region)}"
        feeds[key] = f"https://www.prnewswire.com/{region}/rss/news-releases-list.rss"
        meta[key] = {
            "provider": "pr_newswire",
            "label": _PRNEWSWIRE_REGION_LABELS[region],
        }

    for cat in _PRNEWSWIRE_CATEGORIES:
        if cat in _PRNEWSWIRE_GLOBAL_SKIP:
            continue
        key = f"pr_newswire_global_{_slug(cat)}"
        feeds[key] = (
            f"https://www.prnewswire.com/rss/{cat}-latest-news/{cat}-latest-news-list.rss"
        )
        meta[key] = {
            "provider": "pr_newswire",
            "label": f"Global — {_PRNEWSWIRE_CATEGORY_LABELS[cat]}",
        }

    for region in _PRNEWSWIRE_REGIONS:
        region_label = _PRNEWSWIRE_REGION_LABELS[region]
        for cat in _PRNEWSWIRE_CATEGORIES:
            key = f"pr_newswire_{_slug(region)}_{_slug(cat)}"
            feeds[key] = (
                f"https://www.prnewswire.com/{region}/rss/"
                f"{cat}-latest-news/{cat}-latest-news-list.rss"
            )
            meta[key] = {
                "provider": "pr_newswire",
                "label": f"{region_label} — {_PRNEWSWIRE_CATEGORY_LABELS[cat]}",
            }

    for code, label in _GLOBENEWSWIRE_INDUSTRIES:
        key = _globenewswire_industry_key(label)
        feeds[key] = _globenewswire_industry_url(code, label)
        meta[key] = {
            "provider": "globenewswire",
            "label": f"Industry — {label}",
        }

    for code, label in _GLOBENEWSWIRE_SUBJECTS:
        key = _globenewswire_subject_key(label)
        feeds[key] = _globenewswire_subject_url(code, label)
        meta[key] = {
            "provider": "globenewswire",
            "label": f"Subject — {label}",
        }

    for key, (provider, label, url) in _CURATED_FEEDS.items():
        feeds[key] = url
        meta[key] = {"provider": provider, "label": label}

    return feeds, meta


_DEFAULT_FEEDS, _DEFAULT_META = _build_feed_registry()


def _user_news_config() -> dict | None:
    """Return the ``[news]`` table from ``openbb.toml``."""
    config = load_config()
    if not isinstance(config, dict):
        return None
    news = config.get("news")
    return news if isinstance(news, dict) else None


def _user_feed_entries() -> dict[str, dict[str, str]] | None:
    """Return normalized user feeds keyed by feed id."""
    news = _user_news_config()
    if not news:
        return None
    raw = news.get("rss_feeds")
    if not isinstance(raw, dict) or not raw:
        return None

    out: dict[str, dict[str, str]] = {}
    for key, value in raw.items():
        skey = str(key)
        if isinstance(value, str) and value:
            out[skey] = {
                "url": value,
                "provider": "custom",
                "label": _humanize(skey),
            }
        elif isinstance(value, dict):
            url = value.get("url")
            if not isinstance(url, str) or not url:
                continue
            out[skey] = {
                "url": url,
                "provider": str(value.get("provider") or "custom"),
                "label": str(value.get("label") or _humanize(skey)),
            }
    return out or None


def _user_provider_labels() -> dict[str, str]:
    """Return user-defined provider labels from ``[news.rss_providers]``."""
    news = _user_news_config()
    if not news:
        return {}
    providers = news.get("rss_providers")
    if isinstance(providers, dict):
        return {str(k): str(v) for k, v in providers.items() if isinstance(v, str)}
    return {}


def _should_merge_defaults() -> bool:
    """Return ``True`` when ``[news] merge_defaults = true``."""
    news = _user_news_config()
    return bool(news and news.get("merge_defaults"))


def list_feeds() -> dict[str, str]:
    """Return the active ``{key: url}`` map."""
    user = _user_feed_entries()
    if user is None:
        return dict(_DEFAULT_FEEDS)
    user_urls = {k: v["url"] for k, v in user.items()}
    if _should_merge_defaults():
        merged = dict(_DEFAULT_FEEDS)
        merged.update(user_urls)
        return merged
    return user_urls


def _feed_meta() -> dict[str, dict[str, str]]:
    """Return ``{key: {provider, label}}`` for the active feed set."""
    user = _user_feed_entries()
    if user is None:
        return dict(_DEFAULT_META)
    user_meta = {
        k: {"provider": v["provider"], "label": v["label"]} for k, v in user.items()
    }
    if _should_merge_defaults():
        merged = dict(_DEFAULT_META)
        merged.update(user_meta)
        return merged
    return user_meta


def list_providers() -> dict[str, str]:
    """Return ``{provider_id: label}`` for active providers."""
    user_labels = _user_provider_labels()
    providers_in_use = {entry["provider"] for entry in _feed_meta().values()}
    result: dict[str, str] = {}
    for pid in sorted(providers_in_use):
        if pid in user_labels:
            result[pid] = user_labels[pid]
        elif pid in _PROVIDER_LABELS:
            result[pid] = _PROVIDER_LABELS[pid]
        else:
            result[pid] = _humanize(pid)
    return result


def list_feed_choices(provider: str | None = None) -> list[dict[str, str]]:
    """Return ``[{label, value}]`` for feeds under ``provider``."""
    if not provider:
        return []
    meta = _feed_meta()
    choices = [
        {"label": entry["label"], "value": key}
        for key, entry in meta.items()
        if entry["provider"] == provider
    ]
    return sorted(choices, key=lambda c: c["label"])


def get_feed_url(key: str) -> str:
    """Look up a feed URL by key."""
    feeds = list_feeds()
    url = feeds.get(key)
    if url is None:
        known = ", ".join(sorted(feeds))
        raise ValueError(f"Unknown RSS feed source '{key}'. Known sources: {known}.")
    return url


_DEFAULT_FEED_BY_PROVIDER: dict[str, str] = {
    "axios": "axios_main",
    "bbc": "bbc_world",
    "benzinga": "benzinga_markets",
    "cbc": "cbc_business",
    "fox_news": "fox_news_latest",
    "globenewswire": "globenewswire_all",
    "google_news": "google_news_us",
    "pr_newswire": "pr_newswire_global",
    "wired": "wired_business",
}


def default_feed_for(provider: str | None) -> str | None:
    """Return the default feed key for ``provider``."""
    if not provider:
        return None
    preferred = _DEFAULT_FEED_BY_PROVIDER.get(provider)
    if preferred and preferred in list_feeds():
        return preferred
    choices = list_feed_choices(provider)
    return choices[0]["value"] if choices else None
