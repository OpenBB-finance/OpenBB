"""FR Y-9SP report structure generator."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from openbb_federal_reserve.utils.report_structure import summarize

USER_GUIDE_URL = (
    "https://www.frbservices.org/binaries/content/assets/crsocms/"
    "central-bank/reporting-central/fry-9-sp-upload-user-guide.pdf"
)

CSV_URL = (
    "https://www.ffiec.gov/npw/FinancialReport/ReturnFinancialReportCSV"
    "?rpt=FRY9SP&id={rssd}&dt={date}"
)

SAMPLE_RSSDS: tuple[str, ...] = ("1020395", "2334062")
SAMPLE_DATES: tuple[str, ...] = ("20251231", "20250630", "20241231", "20231231")

ASSET_PATH = (
    Path(__file__).resolve().parent.parent / "assets" / "fry9sp" / "structure.json"
)

_SCHEDULE_NAMES: dict[str, str] = {
    "COVER": "Cover Page",
    "SI": "Schedule SI - Income Statement",
    "SC": "Schedule SC - Balance Sheet",
    "SC-M": "Schedule SC-M - Memoranda",
    "NOTES": "Notes to the Financial Statements",
}

_IDENTITY_NAMES = {
    "INSTITUTION NAME",
    "CITY AND STATE",
    "CITY",
    "STATE",
    "ZIP CODE",
    "STREET ADDRESS",
    "ID_RSSD",
    "REGULATORY DISTRICT",
    "BANK COUNT",
    "TOTAL ASSETS",
    "PEER_GRP",
    "REPORT DATE",
}

_MDRM_NAME = re.compile(r"[A-Z]{4}[A-Z0-9]{4}")

_FORM: tuple[tuple[str, str | None, str, str | None, int, bool], ...] = (
    (
        "COVER",
        None,
        "Printed Name of Chief Financial Officer (or Equivalent)",
        "BHSPC490",
        1,
        False,
    ),
    ("COVER", None, "Date of Signature (MM/DD/YYYY)", "BHSXJ196", 1, False),
    ("COVER", None, "Legal Title of Holding Company", "RSSD9017", 1, False),
    (
        "COVER",
        None,
        "(Mailing Address of the Holding Company) Street / PO Box",
        "RSSD9110",
        1,
        False,
    ),
    ("COVER", None, "City", "RSSD9130", 1, False),
    ("COVER", None, "State", "RSSD9200", 1, False),
    ("COVER", None, "Zip Code", "RSSD9220", 1, False),
    ("COVER", None, "Name / Title", "BHSX8901", 1, False),
    ("COVER", None, "Area Code / Phone Number", "BHSX8902", 1, False),
    ("COVER", None, "Area Code / FAX Number", "BHSX9116", 1, False),
    ("COVER", None, "E-mail Address of Contact", "BHSX4086", 1, False),
    (
        "COVER",
        None,
        "Is confidential treatment requested for any portion of this report submission (0=No, 1=Yes)",
        "BHSPC447",
        1,
        False,
    ),
    (
        "COVER",
        None,
        'If a letter justifying this request is being provided along with the report, enter "1". If a letter justifying this request has been provided separately, enter "0".',
        "BHSPKY38",
        1,
        False,
    ),
    ("COVER", None, "Chief Executive Officer: Name", "BHSPFT42", 1, False),
    (
        "COVER",
        None,
        "Chief Executive Officer: Area Code/Phone Number/EXT",
        "BHSPFT43",
        1,
        False,
    ),
    ("COVER", None, "Chief Executive Officer: Email", "BHSPFT44", 1, False),
    ("SI", "1", "Income from bank subsidary(ies)", None, 1, True),
    ("SI", "1.a", "Dividends", "BHSP0508", 2, False),
    ("SI", "1.b", "Other income", "BHSP2111", 2, False),
    ("SI", "2", "Income from non-bank subsidary(ies)", None, 1, True),
    ("SI", "2.a", "Dividends", "BHSP0523", 2, False),
    ("SI", "2.b", "Other income", "BHSP0530", 2, False),
    ("SI", "3", "Income from subsidiary holding company(ies)", None, 1, True),
    ("SI", "3.a", "Dividends", "BHSP0206", 2, False),
    ("SI", "3.b", "Other income", "BHSP1283", 2, False),
    ("SI", "4", "Other income", "BHSP0447", 1, False),
    (
        "SI",
        "5",
        "TOTAL OPERATING INC (sum of items 1, 2, 3, & 4)",
        "BHSP4000",
        1,
        False,
    ),
    ("SI", "6", "Interest expense", "BHSP4073", 1, False),
    ("SI", "7", "Other expenses", "BHSP4093", 1, False),
    ("SI", "8", "TOTAL OPERATING EXP (sum of items 6 and 7)", "BHSP4130", 1, False),
    (
        "SI",
        "9.a",
        "Income (loss) before unrealized holding gains (losses) on equity securities not held for trading, applicable income taxes, & discontinued ops (item.5 minus 8)",
        "BHSPHT69",
        2,
        False,
    ),
    (
        "SI",
        "9.b",
        "Change in net unrealized holding gains (losses) on equity securites not held for trading.",
        "BHSPHT70",
        2,
        False,
    ),
    (
        "SI",
        "9.c",
        "Income (loss) before applicable income taxes, discontinued operations and undistributed income (sum of items 9.a and 9.b)",
        "BHSP4250",
        2,
        False,
    ),
    (
        "SI",
        "10",
        "Applicable income taxes (benefits) (estimated)",
        "BHSP4302",
        1,
        False,
    ),
    (
        "SI",
        "11",
        "Discontinued ops, net of applicable income taxes",
        "BHSPFT28",
        1,
        False,
    ),
    (
        "SI",
        "12",
        "Income (loss) before undistributed income of subsidiary(ies) (sum of items 9(c) and 11 minus 10)",
        "BHSP0496",
        1,
        False,
    ),
    (
        "SI",
        "13",
        "Equity in undistributed income (loss) of subsidairy(ies):",
        None,
        1,
        True,
    ),
    ("SI", "13.a", "Bank subsidiary(ies)", "BHSP3156", 2, False),
    ("SI", "13.b", "Nonbank subsidiary(ies)", "BHSP2112", 2, False),
    ("SI", "13.c", "Subsidiary holding company(ies)", "BHSP3513", 2, False),
    ("SI", "14", "Net income (loss) (sum of items 12 and 13)", "BHSP4340", 1, False),
    (
        "SI",
        "M.1",
        "Cash dividends (or non-taxable distributions) declared by the holding company to its shareholders",
        "BHSP3158",
        1,
        False,
    ),
    (
        "SI",
        "M.2",
        'Does the reporting holding company have a Subchapter S election in effect for federal income tax purposes for current tax year? (Enter "1" for Yes; enter "0" for No.)',
        "BHSPA530",
        1,
        False,
    ),
    (
        "SI",
        "M.3",
        "Interest expense paid to special-purpose subsidiaries that issued trust preferred sec (included item 7 above)",
        "BHSPC254",
        1,
        False,
    ),
    (
        "SI",
        "M.4",
        "Net change in fair values of financial instruments accounted for under a fair value option",
        "BHSPJ980",
        1,
        False,
    ),
    (
        "SI",
        "M.5",
        'Does your holding company have 100 or more full-time equivalent employees on a consolidated basis? (enter "1" for Yes; leave blank for No)',
        "BHSPMZ36",
        1,
        False,
    ),
    ("SC", "1", "Cash and due from depository institutions:", None, 1, True),
    (
        "SC",
        "1.a",
        "Balances with subsidiary or affiliated depository institutions",
        "BHSP5993",
        2,
        False,
    ),
    (
        "SC",
        "1.b",
        "Balances with unrelated depository institutions",
        "BHSP0010",
        2,
        False,
    ),
    ("SC", "2", "Securities", "BHSP0390", 1, False),
    (
        "SC",
        "3",
        "Loans and lease financing receivables (exclusive of loans and lease financing receivables due from bank(s) and nonbank subsidiaries):",
        None,
        1,
        True,
    ),
    (
        "SC",
        "3.a",
        "Loans and leases, held for investment and held for sale",
        "BHSP2122",
        2,
        False,
    ),
    (
        "SC",
        "3.b",
        "LESS: Allowance for credit losses on loans and leases",
        "BHSP3123",
        2,
        False,
    ),
    (
        "SC",
        "3.c",
        "Loans and leases held for investment and held for sale, net of the allowance for loan and lease losses (item 3.a minus 3.b)",
        "BHSP2723",
        2,
        False,
    ),
    ("SC", "4", "Investment in bank subsidiary(ies):", None, 1, True),
    ("SC", "4.a", "Equity investment", "BHSP3239", 2, False),
    ("SC", "4.b", "Goodwill", "BHSP3238", 2, False),
    (
        "SC",
        "4.c",
        "Loans and advances to and receivables due from bank subsidiary(ies)",
        "BHSP3148",
        2,
        False,
    ),
    ("SC", "5", "Investment in nonbank subsidiary(ies):", None, 1, True),
    ("SC", "5.a", "Equity investment", "BHSP0088", 2, False),
    ("SC", "5.b", "Goodwill", "BHSP0087", 2, False),
    (
        "SC",
        "5.c",
        "Loans and advances to and receivables due from nonbank subsidiary(ies)",
        "BHSP0089",
        2,
        False,
    ),
    (
        "SC",
        "6",
        "Investment in subsidiary holding company(ies) (These items are to be completed only by companies that have subsidiary holding companies):",
        None,
        1,
        True,
    ),
    ("SC", "6.a", "Equity investment", "BHSP0201", 2, False),
    ("SC", "6.b", "Goodwill", "BHSP0202", 2, False),
    (
        "SC",
        "6.c",
        "Loans & advances to & receivables due from sub holding company(ies)",
        "BHSP3523",
        2,
        False,
    ),
    ("SC", "7", "Other assets", "BHSP0027", 1, False),
    (
        "SC",
        "8",
        "Balances due from related nonbank companies (other than investments)",
        "BHSP3620",
        1,
        False,
    ),
    ("SC", "9", "TOTAL ASSETS (sum of items 1 through 8)", "BHSP2170", 1, False),
    ("SC", "10", "Short-term borrowings:", None, 1, True),
    ("SC", "10.a", "Commercial paper", "BHSP2309", 2, False),
    ("SC", "10.b", "Other short-term borrowings", "BHSP2724", 2, False),
    (
        "SC",
        "11",
        "Long-term borrowings (includes limited-life preferred stock and related surplus)",
        "BHSP3151",
        1,
        False,
    ),
    ("SC", "12", "Accrued interest payable (see instructions)", "BHSP3166", 1, False),
    ("SC", "13", "Other liabilities", "BHSP3167", 1, False),
    ("SC", "14", "Balances due to subsidaries and related institutions", None, 1, True),
    ("SC", "14.a", "Subsidiary bank(s)", "BHSP3605", 2, False),
    (
        "SC",
        "14.b",
        "Nonbank subsidiaries and related institutions",
        "BHSP3621",
        2,
        False,
    ),
    ("SC", "15", "Not applicable", None, 1, True),
    ("SC", "16", "Equity Capital", None, 1, True),
    (
        "SC",
        "16.a",
        "Perpetual preferred stock (including related surplus)",
        "BHSP3283",
        2,
        False,
    ),
    ("SC", "16.b", "Common stock (including related surplus)", "BHSP3230", 2, False),
    ("SC", "16.c", "Retained earnings", "BHSP3247", 2, False),
    ("SC", "16.d", "Accumulated other comprehensive income", "BHSPB530", 2, False),
    ("SC", "16.e", "Other equity capital components", "BHSPA130", 2, False),
    (
        "SC",
        "16.f",
        "Total equity capital (sum of items 16.a through 16.e)",
        "BHSP3210",
        2,
        False,
    ),
    (
        "SC",
        "17",
        "TOTAL LIABILITIES & EQUITY CAPITAL (sum of items 10 through 14.b & 16.f)",
        "BHSP3300",
        1,
        False,
    ),
    (
        "SC",
        "M.1",
        'Has the holding company engaged in a full-scope independent external audit at any time during the calendar year (Enter "1" for Yes; enter "0" for No.)',
        "BHSPC884",
        1,
        False,
    ),
    (
        "SC",
        "M.2",
        "If response to Memorandum item 1 is yes, indicate below the name and address of the holding company's independent external auditing firm and the name & email address of the auditing firm's engage partner.",
        None,
        1,
        True,
    ),
    ("SC", "M.2.a.1", "Name of External Auditing Firm", "TEXTC703", 2, False),
    ("SC", "M.2.a.2", "City", "TEXTC708", 2, False),
    ("SC", "M.2.a.3", "State Abbreviation", "TEXTC714", 2, False),
    ("SC", "M.2.a.4", "Zip Code", "TEXTC715", 2, False),
    ("SC", "M.2.b.1", "Name of Engagement Partner", "TEXTC704", 2, False),
    ("SC", "M.2.b.2", "E-mail Address", "TEXTC705", 2, False),
    (
        "SC",
        "M.3",
        "Financial assets and liabilities measured at fair value",
        None,
        1,
        True,
    ),
    ("SC", "M.3.a", "Total assets", "BHSPF819", 2, False),
    ("SC", "M.3.b", "Total liabilities", "BHSPF820", 2, False),
    (
        "SC-M",
        "M.1",
        "Total consolidated assets of the holding company",
        "BHSP8519",
        1,
        False,
    ),
    (
        "SC-M",
        "M.2",
        "Holding company (parent company only) borrowings not held by financial institution(s) or by insiders (including directors) and their interests (included in balance sheet items 10 or 11 above)",
        "BHSP3152",
        1,
        False,
    ),
    (
        "SC-M",
        "M.3",
        "Treasury stock (report only if the amount exceeds 5 percent of equity capital) included in item 16.f above",
        "BHSP3153",
        1,
        False,
    ),
    (
        "SC-M",
        "M.4",
        "Amount of nonvoting equity capital, including related surplus (included in balance sheet items 16.a., 16b., 16.c., and 16.d.)",
        "BHSPC702",
        1,
        False,
    ),
    (
        "SC-M",
        "M.5",
        "Total loans from parent holding company and nonbank subsidiary(ies) to insiders (excluding directors) and their interests",
        "BHSP3155",
        1,
        False,
    ),
    ("SC-M", "M.6", "Pledged securities", "BHSP0416", 1, False),
    (
        "SC-M",
        "M.7.a",
        "Fair value of securities classified as available-for-sale (included in item 2 of the balance sheet)",
        "BHSP8516",
        2,
        False,
    ),
    (
        "SC-M",
        "M.7.b",
        "Amortized cost of securities classified as held-to-maturity (included in item 2 of the balance sheet)",
        "BHSP8517",
        2,
        False,
    ),
    (
        "SC-M",
        "M.7.c",
        "Fair value of equity securities with readily determinable fair values (included in item 2 of the bal sheet)",
        "BHSPHT95",
        2,
        False,
    ),
    (
        "SC-M",
        "M.8.a",
        "Total off-balance-sheet activities conducted either directly or through a nonbank subsidiary",
        "BHSPF074",
        2,
        False,
    ),
    (
        "SC-M",
        "M.8.b",
        "Total debt and equity securities (other than trust preferred securities) outstanding that are registered with the Securities and Exchange Commission",
        "BHSPF075",
        2,
        False,
    ),
    (
        "SC-M",
        "M.9",
        "Balances held by the subsidiary bank(s) due from nonbank subsidiaries of the parent holding company",
        "BHSP6796",
        1,
        False,
    ),
    (
        "SC-M",
        "M.10",
        "Balances held by the subsidiary bank(s) due to nonbank subsidiaries of the parent holding company",
        "BHSP6797",
        1,
        False,
    ),
    (
        "SC-M",
        "M.11",
        "Other assets (only report amounts that exceed 25 percent of balance sheet, line item 7).",
        None,
        1,
        True,
    ),
    ("SC-M", "M.11.a", "Accounts receivable", "BHSPA024", 2, False),
    ("SC-M", "M.11.b", "Income taxes receivable", "BHSPC256", 2, False),
    ("SC-M", "M.11.c", "Premises and fixed assets", "BHSP2145", 2, False),
    ("SC-M", "M.11.d", "Net deferred tax assets", "BHSP2148", 2, False),
    (
        "SC-M",
        "M.11.e",
        "Cash surrender value of life insurance policies",
        "BHSPC009",
        2,
        False,
    ),
    ("SC-M", "M.11.f", "Description", "TEXT8520", 2, False),
    ("SC-M", "M.11.f", "Amount", "BHSP8520", 2, False),
    ("SC-M", "M.11.g", "Description", "TEXT8521", 2, False),
    ("SC-M", "M.11.g", "Amount", "BHSP8521", 2, False),
    ("SC-M", "M.11.h", "Description", "TEXT8522", 2, False),
    ("SC-M", "M.11.h", "Amount", "BHSP8522", 2, False),
    (
        "SC-M",
        "M.12",
        "Other liabilities (only report amounts that exceed 25 percent of balance sheet, line item 13).",
        None,
        1,
        True,
    ),
    ("SC-M", "M.12.a", "Accounts payable", "BHSP3066", 2, False),
    ("SC-M", "M.12.b", "Income taxes payable", "BHSPC257", 2, False),
    ("SC-M", "M.12.c", "Dividends payable", "BHSP2932", 2, False),
    ("SC-M", "M.12.d", "Net deferred tax liabilities", "BHSP3049", 2, False),
    ("SC-M", "M.12.e", "Description", "TEXT8523", 2, False),
    ("SC-M", "M.12.e", "Amount", "BHSP8523", 2, False),
    ("SC-M", "M.12.f", "Description", "TEXT8524", 2, False),
    ("SC-M", "M.12.f", "Amount", "BHSP8524", 2, False),
    ("SC-M", "M.12.g", "Description", "TEXT8525", 2, False),
    ("SC-M", "M.12.g", "Amount", "BHSP8525", 2, False),
    (
        "SC-M",
        "M.13",
        "Notes payable to special-purpose subsidiaries that issued trust preferred sec (included in balance sheet, item 14.b)",
        "BHSPC255",
        1,
        False,
    ),
    (
        "SC-M",
        "M.14",
        "Have there been any changes in investments and activities (acquisitions, divestitures of subsidiaries or other businesses, openings or closings of branches) during the period that have not been reported on the FR Y-6A? If the answer to this question is no, complete the FR Y-10",
        "BHSP6416",
        1,
        False,
    ),
    (
        "SC-M",
        "M.14",
        "Name of holding company official verifying FR Y-10 reporting",
        "TEXT6428",
        1,
        False,
    ),
    ("SC-M", "M.14", "Area Code / Phone Number", "TEXT9009", 1, False),
    (
        "SC-M",
        "M.15",
        "Short-term borrowings included in balance sheet item 14.b",
        None,
        1,
        True,
    ),
    ("SC-M", "M.15.a", "From parent holding company", "BHSP3524", 2, False),
    ("SC-M", "M.15.b", "From subsidiary holding company", "BHSP3526", 2, False),
    (
        "SC-M",
        "M.16",
        "Long-term borrowings included in balance sheet item 14.b",
        None,
        1,
        True,
    ),
    ("SC-M", "M.16.a", "From parent holding company", "BHSP3525", 2, False),
    ("SC-M", "M.16.b", "From subsidiary holding company", "BHSP3527", 2, False),
    (
        "SC-M",
        "M.17.a",
        "Total combined nonbank assets of nonbank subsidiaries",
        "BHSP4778",
        2,
        False,
    ),
    (
        "SC-M",
        "M.17.b",
        "Total combined loans and leases of nonbank subsidiaries",
        "BHSPC427",
        2,
        False,
    ),
    (
        "SC-M",
        "M.17.c",
        "Total aggregate operating revenue of nonbank subsidiaries",
        "BHSPC428",
        2,
        False,
    ),
    (
        "SC-M",
        "M.17.d",
        "Combined thrift assets included in 17.a (to be completed by a bank holding company)",
        "BHSP2792",
        2,
        False,
    ),
    (
        "SC-M",
        "M.17.e",
        "Number of nonbank subsidiaries included in 17.a",
        "BHSP2794",
        2,
        False,
    ),
    (
        "SC-M",
        "M.17.f",
        "Number of thrift subsidiaries included in 17.d (to be completed by a bank holding company)",
        "BHSP2796",
        2,
        False,
    ),
    (
        "SC-M",
        "M.18",
        'Does the holding company hold, either directly or indirectly through a subsidiary or affiliate, any nonfinancial equity investments (see instructions for definition) within a Small Business Investment Company (SBIC) structure, or under section 4(c)(6) or 4(c)(7) of the Bank Holding Company Act, or pursuant to the merchant banking authority of section 4(k)4(H) of the Bank Holding Company Act, or pursuant to the investment authority granted by Regulation K? (Enter "1" for Yes; enter "0" for No.)',
        "BHSPC161",
        1,
        False,
    ),
    (
        "SC-M",
        "M.19",
        'Do your aggregate nonfinancial equity investments (see instructions for definition) equal or exceed (on an acquisition cost basis) 10 percent of the holding company\'s total capital as of the report date? (Enter "1" for Yes; enter "0" for No.)',
        "BHSPC159",
        1,
        False,
    ),
    (
        "SC-M",
        "M.20.a",
        'Has the holding company sold or otherwise liquidated its holding of any nonfinancial equity investment since the previous period? (Enter "1" for Yes; enter "0" for No.)',
        "BHSPC700",
        2,
        False,
    ),
    (
        "SC-M",
        "M.20.b",
        'Does the holding company manage any nonfinancial equity investments for the benefit of others? (Enter "1" for Yes; enter "0" for No.)',
        "BHSPC701",
        2,
        False,
    ),
    (
        "SC-M",
        "M.21",
        "Net assets of broker-dealer subsidiaries engaged in underwriting or dealing securities pursuant to Section 4(k)(4)(E) of the Bank Holding Company Act as amended by the Gramm-Leach-Bliley Act",
        "BHSPC252",
        1,
        False,
    ),
    (
        "SC-M",
        "M.22",
        "Net assets of subsidiaries engaged in insurance or reinsurance underwriting pursuant to Section 4(k)(4)(B) of the Bank Holding Company Act as amended by the Gramm-Leach-Bliley Act",
        "BHSPC253",
        1,
        False,
    ),
    (
        "SC-M",
        "M.23.a",
        "Senior perpetual preferred stock or similar items",
        "BHSPG234",
        2,
        False,
    ),
    (
        "SC-M",
        "M.23.b",
        "Warrants to purchase common stock or similar items",
        "BHSPG235",
        2,
        False,
    ),
    ("NOTES", "1", "Amount - 1", "BHSPK141", 1, False),
    ("NOTES", "2", "Description - 2", "TEXT8527", 1, False),
    ("NOTES", "2", "Amount - 2", "BHSP8527", 1, False),
    ("NOTES", "3", "Description - 3", "TEXT8528", 1, False),
    ("NOTES", "3", "Amount - 3", "BHSP8528", 1, False),
    ("NOTES", "4", "Description - 4", "TEXT8529", 1, False),
    ("NOTES", "4", "Amount - 4", "BHSP8529", 1, False),
    ("NOTES", "5", "Description - 5", "TEXT8530", 1, False),
    ("NOTES", "5", "Amount - 5", "BHSP8530", 1, False),
)


def _fetch_bytes(url: str) -> bytes:
    """Download a canonical source URL as raw bytes."""
    from openbb_federal_reserve.utils.curl_session import get_session

    def warmup(session: Any) -> None:
        session.get("https://www.ffiec.gov/npw/", timeout=30)

    session = get_session("ffiec_nic", warmup)
    response = session.get(
        url, headers={"Referer": "https://www.ffiec.gov/npw/"}, timeout=180
    )
    response.raise_for_status()
    return response.content


def _csv_value_codes(csv_bytes: bytes) -> set[str]:
    """Return the value-bearing MDRM codes in one per-institution CSV."""
    import csv as _csv
    import io

    codes: set[str] = set()
    reader = _csv.reader(io.StringIO(csv_bytes.decode("utf-8-sig", "ignore")))
    for row in reader:
        if len(row) < 3:
            continue
        name = row[0].strip()
        if not name or name.upper() in _IDENTITY_NAMES:
            continue
        if _MDRM_NAME.fullmatch(name):
            codes.add(name)
    return codes


def _filed_union(csv_payloads: list[bytes]) -> set[str]:
    """Union the value-bearing MDRM codes across the sampled CSV payloads."""
    union: set[str] = set()
    for payload in csv_payloads:
        union |= _csv_value_codes(payload)
    return union


def _build_items(filed: set[str]) -> list[dict[str, Any]]:
    """Project the curated form onto the filed item set in form order."""
    keep = [False] * len(_FORM)
    for index, row in enumerate(_FORM):
        if not row[5] and row[3] in filed:
            keep[index] = True

    for index, row in enumerate(_FORM):
        if not row[5]:
            continue
        level = row[4]
        for follower in range(index + 1, len(_FORM)):
            follower_level = _FORM[follower][4]
            if follower_level <= level:
                break
            if not _FORM[follower][5] and keep[follower]:
                keep[index] = True
                break

    items: list[dict[str, Any]] = []
    for index, (schedule, line, caption, mdrm, level, is_header) in enumerate(_FORM):
        if not keep[index]:
            continue
        items.append(
            {
                "schedule": schedule,
                "schedule_name": _SCHEDULE_NAMES[schedule],
                "line": line,
                "caption": caption,
                "mdrm": mdrm,
                "columns": [mdrm] if mdrm else None,
                "level": level,
                "is_header": is_header,
            }
        )
    return items


def validate(items: list[dict[str, Any]], filed: set[str]) -> dict[str, Any]:
    """Compare the structure's value items against the filed-code union."""
    structure_codes = [item["mdrm"] for item in items if item["mdrm"]]
    structure_set = set(structure_codes)
    mapped = filed & structure_set
    missing = sorted(filed - structure_set)
    permanent_empty = sorted(structure_set - filed)
    duplicates = sorted(
        code for code in structure_set if structure_codes.count(code) > 1
    )
    return {
        "csv_code_count": len(filed),
        "mapped_count": len(mapped),
        "missing": missing,
        "permanent_empty": permanent_empty,
        "duplicate_codes": duplicates,
        "coverage": round(100 * len(mapped) / len(filed), 2) if filed else 0.0,
    }


def generate(csv_paths: list[str] | None = None) -> dict[str, Any]:
    """Project the form onto the sampled filings and return the asset payload.

    Parameters
    ----------
    csv_paths : list[str] | None
        Local per-institution validation CSVs. When omitted, every sampled
        ``(rssd, period)`` is fetched from the canonical feed and the
        non-FR-Y-9SP error responses (an institution that does not file the
        report) are skipped.
    """
    if csv_paths:
        payloads = [Path(path).read_bytes() for path in csv_paths]
    else:
        payloads = []
        for rssd in SAMPLE_RSSDS:
            for date in SAMPLE_DATES:
                payload = _fetch_bytes(CSV_URL.format(rssd=rssd, date=date))
                if payload.lstrip().startswith(b"ItemName"):
                    payloads.append(payload)
    filed = _filed_union(payloads)
    items = _build_items(filed)
    payload = summarize(items, USER_GUIDE_URL)
    payload["validation"] = validate(items, filed)
    payload["sampled_filers"] = list(SAMPLE_RSSDS)
    return payload


def write_asset(csv_paths: list[str] | None = None) -> Path:
    """Generate the structure and write it to the committed static asset."""
    payload = generate(csv_paths)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSET_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return ASSET_PATH


def _main() -> None:
    """Command-line entry point for regenerating the asset."""
    import argparse

    parser = argparse.ArgumentParser(description="Regenerate the FR Y-9SP structure.")
    parser.add_argument(
        "--csv", action="append", default=None, help="Local validation CSV path."
    )
    args = parser.parse_args()
    path = write_asset(args.csv)
    payload = json.loads(path.read_text(encoding="utf-8"))
    validation = payload["validation"]
    print(  # noqa: T201
        f"Wrote {path} -> {payload['schedule_count']} schedules, "
        f"{payload['item_count']} items, "
        f"coverage {validation['coverage']}% "
        f"({validation['mapped_count']}/{validation['csv_code_count']}), "
        f"missing {validation['missing']}, "
        f"permanent_empty {len(validation['permanent_empty'])}"
    )


if __name__ == "__main__":  # pragma: no cover - module-as-script entry guard
    _main()
