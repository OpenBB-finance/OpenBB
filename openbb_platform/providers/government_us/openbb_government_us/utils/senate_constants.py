ROOT = "https://efdsearch.senate.gov"
LANDING_PAGE_URL = "{}/search/home/".format(ROOT)
SEARCH_PAGE_URL = "{}/search/".format(ROOT)
REPORTS_URL = "{}/search/report/data/".format(ROOT)

PDF_PREFIX = "/search/view/paper/"
LANDING_PAGE_FAIL = "Failed to fetch filings landing page"

BATCH_SIZE = 100

REPORT_COL_NAMES = [
    "tx_date",
    "file_date",
    "last_name",
    "first_name",
    "order_type",
    "ticker",
    "asset_name",
    "asset_type",
    "tx_amount",
    "notes",
]
