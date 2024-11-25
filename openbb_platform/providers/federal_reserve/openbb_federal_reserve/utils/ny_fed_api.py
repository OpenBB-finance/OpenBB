"""NY Federal Reserve API Utilities."""

# pylint: disable=too-many-arguments,too-many-locals,unused-argument

from typing import Dict, List, Literal, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from pandas import DataFrame, DatetimeIndex, to_datetime

BASE_URL = "https://markets.newyorkfed.org/api"
OPERATION_STATUS = ["announcements", "results"]
DETAILS = ["summary", "details"]
GUIDE_SHEET_TYPES = ["si", "wi", "fs"]
AMBS_OPERATION_TYPES = ["all", "purchases", "sales", "roll", "swap"]
AMBS_SECURITIES = {
    None: "",
    "basket": "Basket",
    "coupon_swap": "Coupon%20Swap",
    "dollar_roll": "Dollar%20Roll",
    "specified_pool": "Specified%20Pool",
    "tba": "TBA",
}
FXS_OPERATION_TYPES = ["all", "usdollar", "nonusdollar"]
FXS_DATE_TYPES = ["all", "trade", "maturity"]
REFERENCE_RATE_TYPES = ["rate", "volume"]
SECURED_RATE_TYPES = ["tgcr", "bgcr", "sofr", "sofrai"]
UNSECURED_RATE_TYPES = ["effr", "obfr"]
REPO_OPERATION_TYPES = ["all", "repo", "reverserepo"]
REPO_OPERATION_METHODS = ["all", "fixed", "single", "multiple"]
REPO_SECURITY_TYPES = ["mbs", "agency", "tsy", "srf"]
REPO_TERM_TYPES = ["overnight", "term"]
LENDING_OPERATION_TYPES = ["all", "seclending", "extensions"]
AGENCY_HOLDING_TYPES = {
    "all": "all",
    "agency_debts": "agency%20debts",
    "mbs": "mbs",
    "cmbs": "cmbs",
}
TREASURY_HOLDING_TYPES = ["all", "bills", "notesbonds", "frn", "tips"]
TREASURY_OPERATION_TYPES = ["all", "purchases", "sales"]
TREASURY_STATUS_TYPES = ["announcements", "results", "operations"]
TREASURY_SECURITY_TYPE = ["agency", "treasury"]
CategoryChoices = Literal[
    "agency_mbs_operations",
    "central_bank_liquidity_swaps_operations",
    "guide_sheets",
    "primary_dealer_statistics",
    "primary_dealer_market_share",
    "reference_rates",
    "repo_and_reverse_repo_operations",
    "securities_lending_operations",
    "soma_holdings",
    "treasury_securities_operations",
]
HoldingTypes = Literal[
    "all_agency",
    "agency_debts",
    "mbs",
    "cmbs",
    "all_treasury",
    "bills",
    "notesbonds",
    "frn",
    "tips",
]
HOLDING_TYPE_CHOICES = [
    "all_agency",
    "agency_debts",
    "mbs",
    "cmbs",
    "all_treasury",
    "bills",
    "notesbonds",
    "frn",
    "tips",
]


def _get_endpoints(
    category: Union[CategoryChoices, None] = None,
    start_date: Optional[str] = "",
    end_date: Optional[str] = "",
    date: Optional[str] = "2022-02-22",
    details: Optional[str] = "details",
    n_operations: Optional[int] = 90,
    operation_status: Optional[str] = "results",
    ambs_operation: Optional[str] = "all",
    ambs_security: Optional[str] = "",
    fxs_operation_type: Optional[str] = "all",
    fxs_date_type: Optional[str] = "",
    fxs_counterparties: Optional[str] = "",
    guide_sheet_types: Optional[str] = "si",
    is_previous: Optional[bool] = False,
    pd_seriesbreak: Optional[str] = "SBN2022",
    pd_timeseries: Optional[str] = "PDSOOS-ABSTOT",
    pd_asof_date: Optional[str] = "2023-03-01",
    rate_type: Optional[str] = "",
    secured_type: Optional[str] = "sofr",
    unsecured_type: Optional[str] = "effr",
    repo_security_type: Optional[str] = "all",
    repo_operation_type: Optional[str] = "all",
    repo_operation_method: Optional[str] = "all",
    repo_term: Optional[str] = "",
    lending_operation: Optional[str] = "all",
    cusips: Optional[str] = "",
    description: Optional[str] = "",
    agency_holding_type: Optional[str] = "all",
    treasury_holding_type: Optional[str] = "all",
    treasury_operation: Optional[str] = "all",
    treasury_status: Optional[str] = "results",
    treasury_security_type: Optional[str] = "",
) -> Dict:
    """Generate URLs to the all, or a category of, endpoints.

    This function is not intended to be used directly.
    """
    is_latest: str = "latest"
    if ambs_security:
        ambs_security = AMBS_SECURITIES[ambs_security]

    if is_previous:
        is_latest = "previous" if is_previous else "latest"

    end_points = {
        "agency_mbs_operations": {
            "latest": BASE_URL + "/ambs/"
            f"{ambs_operation}"
            "/"
            f"{operation_status}"
            "/"
            f"{details}"
            "/latest.json",
            "previous": BASE_URL + "/ambs/"
            f"{ambs_operation}"
            "/"
            f"{operation_status}"
            "/"
            f"{details}"
            "/previous.json",
            "last_two_weeks": BASE_URL + "/ambs/"
            f"{ambs_operation}"
            "/"
            f"{operation_status}"
            "/"
            f"{details}"
            "/lastTwoWeeks.json",
            "last": BASE_URL + "/ambs/"
            f"{ambs_operation}"
            "/"
            f"{operation_status}"
            "/"
            f"{details}"
            "/last/"
            f"{n_operations}"
            ".json",
            "search": BASE_URL + "/ambs/"
            f"{ambs_operation}"
            "/"
            f"{operation_status}"
            "/"
            f"{details}"
            "/search.json?"
            "securities="
            f"{ambs_security}"
            "&desc="
            f"{description}"
            "&cusip="
            f"{cusips}"
            "&startDate="
            f"{start_date}"
            "&endDate="
            f"{end_date}",
        },
        "central_bank_liquidty_swaps_operations": {
            "latest": BASE_URL + "/fxs/" f"{fxs_operation_type}" "/latest.json",
            "last": BASE_URL + "/fxs/"
            f"{fxs_operation_type}"
            "/last/"
            f"{n_operations}"
            ".json",
            "search": BASE_URL + "/fxs/"
            f"{fxs_operation_type}"
            "/search.json"
            "?startDate="
            f"{start_date}"
            "&endDate="
            f"{end_date}"
            "&dateType="
            f"{fxs_date_type}"
            "&counterparties="
            f"{fxs_counterparties}",
            "counterparties": BASE_URL + "/fxs/list/counterparties.json",
        },
        "guide_sheets": BASE_URL + "/guidesheets/"
        f"{guide_sheet_types}"
        "/"
        f"{is_latest}"
        ".json",
        "primary_dealer_statistics": {
            "latest": BASE_URL + "/pd/latest/" f"{pd_seriesbreak}" ".json",
            "all_timeseries": BASE_URL + "/pd/get/all/timeseries.csv",
            "list_descriptions": BASE_URL + "/pd/list/timeseries.json",
            "list_asof": BASE_URL + "/pd/list/asof.json",
            "list_seriesbreaks": BASE_URL + "/pd/list/seriesbreaks.json",
            "get_asof": BASE_URL + "/pd/get/asof/" f"{pd_asof_date}" ".json",
            "get_timeseries": BASE_URL + "/pd/get/" f"{pd_timeseries}" ".json",
            "get_timeseries_seriesbreak": BASE_URL + "/pd/get/"
            f"{pd_seriesbreak}"
            "/timeseries/"
            f"{pd_timeseries}"
            ".json",
        },
        "primary_dealer_market_share": {
            "quarterly": BASE_URL + "/marketshare/qtrly/latest.xlsx",
            "ytd": BASE_URL + "/marketshare/ytd/latest.xlsx",
        },
        "reference_rates": {
            "latest": BASE_URL + "/rates/all/latest.json",
            "search": BASE_URL + "/rates/all/search.json?"
            "startDate="
            f"{start_date}"
            "&endDate="
            f"{end_date}"
            "&type="
            f"{rate_type}",
            "latest_secured": BASE_URL + "/rates/secured/all/latest.json",
            "latest_unsecured": BASE_URL + "/rates/unsecured/all/latest.json",
            "last_secured": BASE_URL + "/rates/secured/"
            f"{secured_type}"
            "/last/"
            f"{n_operations}"
            ".json",
            "last_unsecured": BASE_URL + "/rates/unsecured/"
            f"{unsecured_type}"
            "/last/"
            f"{n_operations}"
            ".json",
        },
        "repo_and_reverse_repo_operations": {
            "latest": BASE_URL + "/rp/"
            f"{repo_operation_type}"
            "/"
            f"{repo_operation_method}"
            "/"
            f"{operation_status}"
            "/latest.json",
            "last_two_weeks": BASE_URL + "/rp/"
            f"{repo_operation_type}"
            "/"
            f"{repo_operation_method}"
            "/"
            f"{operation_status}"
            "/lastTwoWeeks.json",
            "last": BASE_URL + "/rp/"
            f"{repo_operation_type}"
            "/"
            f"{repo_operation_method}"
            "/"
            f"{operation_status}"
            "/last/"
            f"{n_operations}"
            ".json",
            "search": BASE_URL + "/rp/results/search.json?"
            "startDate="
            f"{start_date}"
            "&endDate="
            f"{end_date}"
            "&operationTypes="
            f"{repo_operation_type}"
            "&method="
            f"{repo_operation_method}"
            "&securityType="
            f"{repo_security_type}"
            "&term="
            f"{repo_term}",
            "propositions": BASE_URL + "/rp/reverserepo/propositions/search.json?"
            "startDate="
            f"{start_date}"
            "&endDate="
            f"{end_date}",
        },
        "securities_lending_operations": {
            "latest": BASE_URL + "/seclending/"
            f"{lending_operation}"
            "/results/"
            f"{details}"
            "/latest.json",
            "last_two_weeks": BASE_URL + "/seclending/"
            f"{lending_operation}"
            "/results/"
            f"{details}"
            "/lastTwoWeeks.json",
            "last": BASE_URL + "/seclending/"
            f"{lending_operation}"
            "/results/"
            f"{details}"
            "/last/"
            f"{n_operations}"
            ".json",
            "search": BASE_URL + "/seclending/"
            f"{lending_operation}"
            "/results/"
            f"{details}"
            "/search.json"
            "?startDate="
            f"{start_date}"
            "&endDate="
            f"{end_date}"
            "&cusips="
            f"{cusips}"
            "&descriptions="
            f"{description}",
        },
        "soma_holdings": {
            "summary": BASE_URL + "/soma/summary.json",
            "release_log": BASE_URL + "/soma/agency/get/release_log.json",
            "list_as_of": BASE_URL + "/soma/asofdates/list.json",
            "get_as_of": BASE_URL + "/soma/agency/get/asof/" f"{date}" ".json",
            "get_cusip": BASE_URL + "/soma/agency/get/cusip/" f"{cusips}" ".json",
            "get_holding_type": BASE_URL + "/soma/agency/get/"
            f"{agency_holding_type}"
            "/asof/"
            f"{date}"
            ".json",
            "agency_debts": BASE_URL + "/soma/agency/wam/agency%20debts/asof/"
            f"{date}"
            ".json",
            "list_release_dates": BASE_URL + "/soma/tsy/get/release_log.json",
            "get_treasury_as_of": BASE_URL + "/soma/tsy/get/asof/" f"{date}" ".json",
            "get_treasury_cusip": BASE_URL + "/soma/tsy/get/cusip/" f"{cusips}" ".json",
            "get_treasury_holding_type": BASE_URL + "/soma/tsy/get/"
            f"{treasury_holding_type}"
            "/asof/"
            f"{date}"
            ".json",
            "get_treasury_debts": BASE_URL + "/soma/tsy/wam/"
            f"{treasury_holding_type}"
            "/asof/"
            f"{date}"
            ".json",
            "get_treasury_monthly": BASE_URL + "/soma/tsy/get/monthly.json",
        },
        "treasury_securities_operations": {
            "current": BASE_URL + "/tsy/"
            f"{treasury_operation}"
            "/"
            f"{treasury_status}"
            "/"
            f"{details}"
            "/latest.json",
            "last_two_weeks": BASE_URL + "/tsy/"
            f"{treasury_operation}"
            "/results/"
            f"{details}"
            "/lastTwoWeeks.json",
            "last": BASE_URL + "/tsy/"
            f"{treasury_operation}"
            "/results/"
            f"{details}"
            "/last/"
            f"{n_operations}"
            ".json",
            "search": BASE_URL + "/tsy/"
            f"{treasury_operation}"
            "/results/"
            f"{details}"
            "/search.json?"
            "startDate="
            f"{start_date}"
            "&endDate="
            f"{end_date}"
            "&securityType="
            f"{treasury_security_type}"
            "&cusip="
            f"{cusips}"
            "&desc="
            f"{description}",
        },
    }
    return end_points if category is None else end_points[category]  # type: ignore


async def fetch_data(url: str) -> Dict:
    """Fetch the JSON response from the API."""
    try:
        response = await amake_request(url)
    except Exception as e:  # pylint: disable=broad-except
        raise e from e
    return response  # type: ignore


def get_nearest_date(dates: List[str], target_date: str) -> str:
    """Get the nearest date in the list of dates to the target date."""
    df = DataFrame(dates, columns=["dates"])
    df["dates"] = DatetimeIndex(df["dates"])
    target_date = to_datetime(target_date)
    differences = (df.dates - target_date).abs()
    nearest_date_index = differences.argmin()
    nearest_date = df.index[nearest_date_index]
    return df.iloc[nearest_date]["dates"].strftime("%Y-%m-%d")


class SomaHoldings:
    """Wrapper for NY Fed's System Open Market Account endpoints.

    All get methods are asynchronous.

    Methods
    -------
    get_as_of_dates: Function for getting all valid as-of dates for SOMA data.
        Returns: List
    get_release_log: Function for getting the last three months of Agency release and as-of dates.
        Returns: List[Dict]
    get_summary: Function for getting historical weekly summaries by holding type.
        Returns: List[Dict]
    get_agency_holdings: Function for getting the latest agency holdings, or as of a single date.
        Returns: List[Dict]
    get_treasury_holdings: Function for getting the latest Treasury holdings, or as-of a single date.
        Returns: List[Dict]

    Examples
    --------
    >>> soma = SomaHoldings()

    >>> logs = await soma.get_release_log()

    >>> mbs = await soma.get_agency_holdings(holding_type = "mbs")

    >>> monthly_holdings = await soma.get_treasury_holdings(monthly = True)
    """

    def __init__(self) -> None:
        """Initialize the SomaHoldings class."""

    def __repr__(self) -> str:
        """Replace original repr with docstring."""
        return str(self.__doc__)

    async def get_as_of_dates(self) -> List:
        """Get all valid as-of dates for SOMA operations."""
        dates_url = _get_endpoints()["soma_holdings"]["list_as_of"]
        dates_response = await fetch_data(dates_url)
        dates = dates_response.get("soma", {}).get("asOfDates", [])
        if not dates:
            raise OpenBBError("Error requesting dates. Please try again later.")
        return dates

    async def get_release_log(
        self,
        treasury: bool = False,
    ) -> List[Dict]:
        """Return the last three months Agency Release and as-of dates.

        Parameters
        ----------
        treasury: bool
            If True, returns the last three months of Treasury release and as-of dates.

        Returns
        -------
        List[Dict]: Dictionary of the release date and as-of dates.

        Example
        -------
        >>> release_log = await SomaHoldings().get_release_log(treasury = True)
        """
        url = (
            _get_endpoints()["soma_holdings"]["list_release_dates"]
            if treasury is True
            else _get_endpoints()["soma_holdings"]["release_log"]
        )
        response = await fetch_data(url)
        release_log = response.get("soma", {}).get("dates", [])
        if not release_log:
            raise OpenBBError("No data found. Try again later.")

        return release_log

    async def get_summary(self) -> List[Dict]:
        """Return historical weekly summary by holding type.

        Returns
        -------
        List[Dict]: Historical weekly summary by holding type.

        Example
        -------
        summary = await SomaHoldings().get_summary()
        """
        url = _get_endpoints()["soma_holdings"]["summary"]
        response = await fetch_data(url)
        summary = response.get("soma", {}).get("summary", [])
        if not summary:
            raise EmptyDataError(
                "There was an error with the request and was returned empty."
            )

        return summary

    async def get_agency_holdings(
        self,
        as_of: Optional[str] = None,
        cusip: Optional[str] = None,
        holding_type: Optional[str] = None,
        wam: bool = False,
    ) -> List[Dict]:
        """Get the latest agency holdings, or as of a single date. Data is updated weekly.

        Parameters
        ----------
        as_of: Optional[str]
            The as-of date to get data for. Defaults to the latest.
        cusip: Optional[str]
            The CUSIP of the security to search for. This parameter takes priority over `holding_type`.
        holding_type: Optional[str]
            The holding type for which to retrieve. Choices are: ['all', 'agency debts', 'mbs', 'cmbs']
        wam: Optional[bool]
            Whether to return a single date weighted average maturity for Agency debt. Defaults to False.
            This parameter takes priority over `holding_type` and `cusip`.

        Returns
        -------
        List[Dict]: List of dictionaries with results.

        Examples
        --------
        >>> holdings = await SomaHoldings().get_agency_holdings(holding_type = "cmbs")

        >>> df = await SomaHoldings().get_agency_holdings(cusip = "3138LMCK7")

        >>> wam = await SomaHoldings().get_agency_holdings(wam = True)
        """
        response: Dict = {}
        url: str = ""
        dates = await self.get_as_of_dates()
        if as_of is not None:
            as_of = get_nearest_date(dates, as_of)
        if as_of is None:
            as_of = dates[0]
        if wam is True:
            url = _get_endpoints(
                date=as_of,
            )[
                "soma_holdings"
            ]["agency_debts"]
            response = await fetch_data(url)
            return [response.get("soma", {})]
        url = _get_endpoints(date=as_of)["soma_holdings"]["get_as_of"]
        if holding_type is not None:
            if holding_type not in AGENCY_HOLDING_TYPES:
                raise OpenBBError(
                    "Invalid choice. Choose from: ['all', 'agency debts', 'mbs', 'cmbs']"
                )
            url = _get_endpoints(
                agency_holding_type=AGENCY_HOLDING_TYPES[holding_type], date=as_of
            )["soma_holdings"]["get_holding_type"]
        if cusip is not None:
            url = _get_endpoints(cusips=cusip)["soma_holdings"]["get_cusip"]
        response = await fetch_data(url)
        holdings = response.get("soma", {}).get("holdings", [])
        if not holdings:
            raise EmptyDataError()

        return holdings

    async def get_treasury_holdings(
        self,
        as_of: Optional[str] = None,
        cusip: Optional[str] = None,
        holding_type: Optional[str] = None,
        wam: Optional[bool] = False,
        monthly: Optional[bool] = False,
    ) -> List[Dict]:
        """Get the latest Treasury holdings, or as of a single date.

        Parameters
        ----------
        as_of: Optional[str]
            The as-of date to get data for. Defaults to the latest.
        cusip: Optional[str]
            The CUSIP of the security to search for. This parameter takes priority over `monthly` and `holding_type`.
        holding_type: Optional[str]
            The holding type for which to retrieve. Choices are: ['all', 'bills', 'notesbonds', 'frn', 'tips']
        wam: Optional[bool]
            Whether to return a single date weighted average maturity for Agency debt. Defaults to False.
            This parameter takes priority over `holding_type`, `cusip`, and `monthly`.
        monthly: Optional[bool]
            If true, returns historical data for all securities at a monthly interval.
            This parameter takes priority over other parameters except `wam`.

        Returns
        -------
        List[Dict]: List of dictionaries with results.

        Examples
        --------
        >>> holdings = await SomaHoldings().get_treasury_holdings(holding_type = "tips")

        >>> df = await SomaHoldings().get_treasury_holdings(cusip = "912810FH6")

        >>> wam = await SomaHoldings().get_treasury_holdings(wam = True)

        >>> monthly = await SomaHoldings().get_treasury_holdings(monthly = True, holding_type = "bills")
        """
        response: Dict = {}
        url: str = ""
        dates = await self.get_as_of_dates()
        if as_of is not None:
            as_of = get_nearest_date(dates, as_of)
        if as_of is None:
            as_of = dates[0]
        if wam is True:
            url = _get_endpoints(
                date=as_of,
            )[
                "soma_holdings"
            ]["get_treasury_debts"]
            response = await fetch_data(url)
            return [response.get("soma", {})]

        if holding_type is not None:
            if holding_type not in TREASURY_HOLDING_TYPES:
                raise OpenBBError(
                    f"Invalid choice. Choose from: {', '.join(TREASURY_HOLDING_TYPES)}"
                )
            url = _get_endpoints(treasury_holding_type=holding_type, date=as_of)[
                "soma_holdings"
            ]["get_treasury_holding_type"]
        if monthly:
            url = _get_endpoints()["soma_holdings"]["get_treasury_monthly"]
        if cusip is not None:
            url = _get_endpoints(cusips=cusip)["soma_holdings"]["get_treasury_cusip"]

        response = await fetch_data(url)
        holdings = response.get("soma", {}).get("holdings", [])
        if not holdings:
            raise EmptyDataError()

        return holdings
