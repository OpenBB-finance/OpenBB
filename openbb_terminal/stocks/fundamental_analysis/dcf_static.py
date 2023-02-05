""" DCF Static """
__docformat__ = "numpy"
from typing import Dict, List

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from openbb_terminal.helper_funcs import excel_columns, get_user_agent

letters = excel_columns()

non_gaap_is = [
    "Revenue Growth",
    "Net Income Common",
    "Net Income Growth",
    "Shares Outstanding (Basic)",
    "Shares Outstanding (Diluted)",
    "Shares Change",
    "EPS (Basic)",
    "EPS (Diluted)",
    "EPS Growth",
    "Free Cash Flow Per Share",
    "Dividend Per Share",
    "Dividend Growth",
    "Gross Margin",
    "Operating Margin",
    "Profit Margin",
    "Free Cash Flow Margin",
    "Effective Tax Rate",
    "EBITDA",
    "EBITDA Margin",
    "EBIT",
    "EBIT Margin",
    "Operating Expenses",
    "Pretax Income",
    "Revenue Growth (YoY)",
    "Depreciation & Amortization",
]
gaap_is = [
    "Revenue",
    "Cost of Revenue",
    "Gross Profit",
    "Selling, General & Admin",
    "Research & Development",
    "Other Operating Expenses",
    "Operating Income",
    "Interest Expense / Income",
    "Other Expense / Income",
    "Income Tax",
    "Net Income",
    "Preferred Dividends",
]
non_gaap_bs = [
    "Cash Growth",
    "Debt Growth",
    "Net Cash / Debt",
    "Net Cash / Debt Growth",
    "Net Cash Per Share",
    "Working Capital",
    "Book Value Per Share",
    "Total Debt",
]
gaap_bs = [
    "Cash & Equivalents",
    "Short-Term Investments",
    "Cash & Cash Equivalents",
    "Receivables",
    "Inventory",
    "Other Current Assets",
    "Total Current Assets",
    "Property, Plant & Equipment",
    "Long-Term Investments",
    "Goodwill and Intangibles",
    "Other Long-Term Assets",
    "Total Long-Term Assets",
    "Total Assets",
    "Accounts Payable",
    "Deferred Revenue",
    "Current Debt",
    "Other Current Liabilities",
    "Total Current Liabilities",
    "Long-Term Debt",
    "Other Long-Term Liabilities",
    "Total Long-Term Liabilities",
    "Total Liabilities",
    "Common Stock",
    "Retained Earnings",
    "Comprehensive Income",
    "Shareholders' Equity",
    "Total Liabilities and Equity",
]
non_gaap_cf = [
    "Operating Cash Flow Growth",
    "Free Cash Flow Growth",
    "Free Cash Flow Margin",
    "Free Cash Flow Per Share",
    "Free Cash Flow",
]
gaap_cf = [
    "Net Income",
    "Depreciation & Amortization",
    "Share-Based Compensation",
    "Other Operating Activities",
    "Operating Cash Flow",
    "Capital Expenditures",
    "Acquisitions",
    "Change in Investments",
    "Other Investing Activities",
    "Investing Cash Flow",
    "Dividends Paid",
    "Share Issuance / Repurchase",
    "Debt Issued / Paid",
    "Other Financing Activities",
    "Financing Cash Flow",
    "Net Cash Flow",
]
sum_rows = [
    "Gross Profit",
    "Operating Income",
    "Net Income",
    "Cash & Cash Equivalents",
    "Total Current Assets",
    "Total Long-Term Assets",
    "Total Assets",
    "Total Current Liabilities",
    "Total Long-Term Liabilities",
    "Total Liabilities",
    "Shareholders' Equity",
    "Total Liabilities and Equity",
    "Operating Cash Flow",
    "Investing Cash Flow",
    "Financing Cash Flow",
    "Net Cash Flow",
]
bold_font = Font(bold=True)
thin_border_top = Border(top=Side(style="thin"))
thin_border_bottom = Border(bottom=Side(style="thin"))

thin_border_nl = Border(
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

thin_border_nr = Border(
    left=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

thin_border = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

green_bg = PatternFill(fgColor="7fe5cd", fill_type="solid")

center = Alignment(horizontal="center")

red = Font(color="FF0000")

fmt_acct = "_($* #,##0.00_);[Red]_($* (#,##0.00);_($* -_0_0_);_(@"

statement_titles = {"BS": "Balance Sheet", "CF": "Cash Flows", "IS": "Income Statement"}

statement_url: Dict[str, str] = {
    "BS": "balance-sheet/",
    "CF": "cash-flow-statement/",
    "IS": "",
}

statement_ignore: Dict[str, List[str]] = {
    "BS": non_gaap_bs,
    "CF": non_gaap_cf,
    "IS": non_gaap_is,
}


headers = {"User-Agent": get_user_agent()}
