"""NY Federal Reserve API Utilities."""

# pylint: disable=too-many-arguments,too-many-locals,unused-argument

from typing import Literal

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


def _get_endpoints(  # pylint: disable=R0917
    category: CategoryChoices | None = None,
    start_date: str | None = "",
    end_date: str | None = "",
    date: str | None = "2022-02-22",
    details: str | None = "details",
    n_operations: int | None = 90,
    operation_status: str | None = "results",
    ambs_operation: str | None = "all",
    ambs_security: str | None = "",
    fxs_operation_type: str | None = "all",
    fxs_date_type: str | None = "",
    fxs_counterparties: str | None = "",
    guide_sheet_types: str | None = "si",
    is_previous: bool | None = False,
    pd_seriesbreak: str | None = "SBN2022",
    pd_timeseries: str | None = "PDSOOS-ABSTOT",
    pd_asof_date: str | None = "2023-03-01",
    rate_type: str | None = "",
    secured_type: str | None = "sofr",
    unsecured_type: str | None = "effr",
    repo_security_type: str | None = "all",
    repo_operation_type: str | None = "all",
    repo_operation_method: str | None = "all",
    repo_term: str | None = "",
    lending_operation: str | None = "all",
    cusips: str | None = "",
    description: str | None = "",
    agency_holding_type: str | None = "all",
    treasury_holding_type: str | None = "all",
    treasury_operation: str | None = "all",
    treasury_status: str | None = "results",
    treasury_security_type: str | None = "",
) -> dict:
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
            "latest": BASE_URL
            + f"/ambs/{ambs_operation}/{operation_status}/{details}/latest.json",
            "previous": BASE_URL
            + f"/ambs/{ambs_operation}/{operation_status}/{details}/previous.json",
            "last_two_weeks": BASE_URL
            + f"/ambs/{ambs_operation}/{operation_status}/{details}/lastTwoWeeks.json",
            "last": BASE_URL
            + f"/ambs/{ambs_operation}/{operation_status}/{details}/last/{n_operations}.json",
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
            "latest": BASE_URL + f"/fxs/{fxs_operation_type}/latest.json",
            "last": BASE_URL + f"/fxs/{fxs_operation_type}/last/{n_operations}.json",
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
        "guide_sheets": BASE_URL + f"/guidesheets/{guide_sheet_types}/{is_latest}.json",
        "primary_dealer_statistics": {
            "latest": BASE_URL + f"/pd/latest/{pd_seriesbreak}.json",
            "all_timeseries": BASE_URL + "/pd/get/all/timeseries.csv",
            "list_descriptions": BASE_URL + "/pd/list/timeseries.json",
            "list_asof": BASE_URL + "/pd/list/asof.json",
            "list_seriesbreaks": BASE_URL + "/pd/list/seriesbreaks.json",
            "get_asof": BASE_URL + f"/pd/get/asof/{pd_asof_date}.json",
            "get_timeseries": BASE_URL + f"/pd/get/{pd_timeseries}.json",
            "get_timeseries_seriesbreak": BASE_URL
            + f"/pd/get/{pd_seriesbreak}/timeseries/{pd_timeseries}.json",
        },
        "primary_dealer_market_share": {
            "quarterly": BASE_URL + "/marketshare/qtrly/latest.xlsx",
            "ytd": BASE_URL + "/marketshare/ytd/latest.xlsx",
        },
        "reference_rates": {
            "latest": BASE_URL + "/rates/all/latest.json",
            "search": BASE_URL
            + f"/rates/all/search.json?startDate={start_date}&endDate={end_date}&type={rate_type}",
            "latest_secured": BASE_URL + "/rates/secured/all/latest.json",
            "latest_unsecured": BASE_URL + "/rates/unsecured/all/latest.json",
            "last_secured": BASE_URL
            + f"/rates/secured/{secured_type}/last/{n_operations}.json",
            "last_unsecured": BASE_URL
            + f"/rates/unsecured/{unsecured_type}/last/{n_operations}.json",
        },
        "repo_and_reverse_repo_operations": {
            "latest": BASE_URL
            + f"/rp/{repo_operation_type}/{repo_operation_method}/{operation_status}/latest.json",
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
            "latest": BASE_URL
            + f"/seclending/{lending_operation}/results/{details}/latest.json",
            "last_two_weeks": BASE_URL
            + f"/seclending/{lending_operation}/results/{details}/lastTwoWeeks.json",
            "last": BASE_URL
            + f"/seclending/{lending_operation}/results/{details}/last/{n_operations}.json",
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
            "get_as_of": BASE_URL + f"/soma/agency/get/asof/{date}.json",
            "get_cusip": BASE_URL + f"/soma/agency/get/cusip/{cusips}.json",
            "get_holding_type": BASE_URL
            + f"/soma/agency/get/{agency_holding_type}/asof/{date}.json",
            "agency_debts": BASE_URL
            + f"/soma/agency/wam/agency%20debts/asof/{date}.json",
            "list_release_dates": BASE_URL + "/soma/tsy/get/release_log.json",
            "get_treasury_as_of": BASE_URL + f"/soma/tsy/get/asof/{date}.json",
            "get_treasury_cusip": BASE_URL + f"/soma/tsy/get/cusip/{cusips}.json",
            "get_treasury_holding_type": BASE_URL
            + f"/soma/tsy/get/{treasury_holding_type}/asof/{date}.json",
            "get_treasury_debts": BASE_URL
            + f"/soma/tsy/wam/{treasury_holding_type}/asof/{date}.json",
            "get_treasury_monthly": BASE_URL + "/soma/tsy/get/monthly.json",
        },
        "treasury_securities_operations": {
            "current": BASE_URL
            + f"/tsy/{treasury_operation}/{treasury_status}/{details}/latest.json",
            "last_two_weeks": BASE_URL
            + f"/tsy/{treasury_operation}/results/{details}/lastTwoWeeks.json",
            "last": BASE_URL
            + f"/tsy/{treasury_operation}/results/{details}/last/{n_operations}.json",
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


async def fetch_data(url: str) -> dict:
    """Fetch the JSON response from the API."""
    try:
        response = await amake_request(url, timeout=30)
    except Exception as e:  # pylint: disable=broad-except
        raise e from e
    return response  # type: ignore


def get_nearest_date(dates: list[str], target_date: str) -> str:
    """Get the nearest date in the list of dates to the target date."""
    df = DataFrame(dates, columns=["dates"])
    df["dates"] = DatetimeIndex(df["dates"])
    target_date = to_datetime(target_date)  # type: ignore
    differences = (df.dates - target_date).abs()  # type: ignore
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

    async def get_as_of_dates(self) -> list:
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
    ) -> list[dict]:
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

    async def get_summary(self) -> list[dict]:
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
        as_of: str | None = None,
        cusip: str | None = None,
        holding_type: str | None = None,
        wam: bool = False,
    ) -> list[dict]:
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
        response: dict = {}
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

    async def get_treasury_holdings(  # pylint: disable=R0917
        self,
        as_of: str | None = None,
        cusip: str | None = None,
        holding_type: str | None = None,
        wam: bool | None = False,
        monthly: bool | None = False,
    ) -> list[dict]:
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
        response: dict = {}
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
