import aiohttp
import asyncio

import pandas as pd
from bs4 import BeautifulSoup
from typing import Any, List, Optional
from openbb_government_us.utils.senate_constants import LANDING_PAGE_URL, LANDING_PAGE_FAIL, SEARCH_PAGE_URL, REPORTS_URL,\
                ROOT, REPORT_COL_NAMES, PDF_PREFIX, BATCH_SIZE

async def _csrf(client: aiohttp.ClientSession) -> str:
    """Set the session ID and return the CSRF token for this session."""
    async with client.get(LANDING_PAGE_URL) as landing_page_response:
        landing_page_text = await landing_page_response.text()
        landing_page = BeautifulSoup(landing_page_text, "lxml")
        form_csrf = landing_page.find(attrs={"name": "csrfmiddlewaretoken"})["value"]
        form_payload = {"csrfmiddlewaretoken": form_csrf, "prohibition_agreement": "1"}
        await client.post(
            LANDING_PAGE_URL, data=form_payload, headers={"Referer": LANDING_PAGE_URL}
        )

    cookies = client.cookie_jar.filter_cookies(LANDING_PAGE_URL)
    csrftoken = cookies.get("csrftoken") or cookies.get("csrf")
    return csrftoken.value if csrftoken else None


async def get_total_reports(client: aiohttp.ClientSession, token: str) -> int:
    """Fetch the total number of reports to determine the number of batches."""
    login_data = {
        "start": "0",
        "length": "100",
        "report_types": "[11]",
        "filer_types": "[]",
        "submitted_start_date": "01/01/2012 00:00:00",
        "submitted_end_date": "",
        "candidate_state": "",
        "senator_state": "",
        "office_id": "",
        "first_name": "",
        "last_name": "",
        "csrfmiddlewaretoken": token,
    }
    async with client.post(
        REPORTS_URL, data=login_data, headers={"Referer": SEARCH_PAGE_URL}
    ) as response:
        response_json = await response.json()
    return response_json["recordsTotal"]


async def senator_reports(client: aiohttp.ClientSession) -> List[List[str]]:
    """Return all results from the periodic transaction reports API."""
    token = await _csrf(client)
    total_reports = await get_total_reports(client, token)
    num_batches = (
        total_reports + BATCH_SIZE - 1
    ) // BATCH_SIZE  # Calculate the number of batches

    tasks = [reports_api(client, idx * BATCH_SIZE, token) for idx in range(num_batches)]

    # Gather all tasks and collect results
    results = await asyncio.gather(*tasks)
    all_reports = [report for batch in results for report in batch]

    return all_reports


async def reports_api(
    client: aiohttp.ClientSession, offset: int, token: str
) -> List[List[str]]:
    """Query the periodic transaction reports API."""
    login_data = {
        "start": str(offset),
        "length": str(BATCH_SIZE),
        "report_types": "[11]",
        "filer_types": "[]",
        "submitted_start_date": "01/01/2012 00:00:00",
        "submitted_end_date": "",
        "candidate_state": "",
        "senator_state": "",
        "office_id": "",
        "first_name": "",
        "last_name": "",
        "csrfmiddlewaretoken": token,
    }
    async with client.post(
        REPORTS_URL, data=login_data, headers={"Referer": SEARCH_PAGE_URL}
    ) as response:
        response_json = await response.json()
    return response_json["data"]


async def _tbody_from_link(
    client: aiohttp.ClientSession, link: str, token: str
) -> Optional[Any]:
    """
    Return the tbody element containing transactions for this senator.
    Return None if no such tbody element exists.
    """
    report_url = "{0}{1}".format(ROOT, link)
    async with client.get(report_url) as report_response:
        # If the page is redirected, then the session ID has expired
        if report_response.url == LANDING_PAGE_URL:
            token = await _csrf(client)  # pylint: disable=unused-variable # noqa
            async with client.get(report_url) as report_response:
                report_text = await report_response.text()
        else:
            report_text = await report_response.text()

    report = BeautifulSoup(report_text, "lxml")
    tbodies = report.find_all("tbody")
    if len(tbodies) == 0:
        return None
    return tbodies[0]


async def txs_for_report(
    client: aiohttp.ClientSession, row: List[str], token: str
) -> pd.DataFrame:
    """
    Convert a row from the periodic transaction reports API to a DataFrame
    of transactions.
    """
    first, last, _, link_html, date_received = row
    link = BeautifulSoup(link_html, "lxml").a.get("href")
    # We cannot parse PDFs
    if link[: len(PDF_PREFIX)] == PDF_PREFIX:
        return pd.DataFrame()

    tbody = await _tbody_from_link(client, link, token)
    if not tbody:
        return pd.DataFrame()

    stocks = []
    for table_row in tbody.find_all("tr"):
        cols = [c.get_text() for c in table_row.find_all("td")]
        tx_date, ticker, asset_name, asset_type, order_type, tx_amount, description = (
            cols[1],
            cols[3],
            cols[4],
            cols[5],
            cols[6],
            cols[7],
            cols[8],
        )
        stocks.append(
            [
                tx_date,
                date_received,
                last,
                first,
                order_type,
                ticker,
                asset_name,
                asset_type,
                tx_amount,
                description,
            ]
        )
    df = pd.DataFrame(stocks, columns=REPORT_COL_NAMES)
    for col in df:
        df[col] = df[col].apply(lambda x: x.replace("\n", "").replace(",", "").strip())

    return df


async def fetch_all_txs(
    client: aiohttp.ClientSession, reports: List[List[str]], token: str
) -> pd.DataFrame:
    """Fetch all transactions concurrently."""
    tasks = [txs_for_report(client, row, token) for row in reports]
    all_transactions = await asyncio.gather(*tasks)
    all_transactions_df = pd.concat(all_transactions, ignore_index=True)
    return all_transactions_df.to_dict('records')


async def get_transactions(num_reports:int):
    session = aiohttp.ClientSession()
    token = await _csrf(session)
    reports = await senator_reports(session)

    return await fetch_all_txs(session, reports[:num_reports], token)

def senate_runner(num_reports:int = 10):
    with asyncio.Runner() as runner:
        print(runner.run(get_transactions(num_reports=num_reports)))

