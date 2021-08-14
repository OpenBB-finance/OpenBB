""" DCF Model """
__docformat__ = "numpy"

from typing import List, Union

import pandas as pd
from openpyxl.styles import Border, Side, Font, PatternFill, Alignment
from openpyxl import worksheet

opts = Union[int, str, float]


def string_float(string: str):
    """Numpy vectorize function to convert strings to floats"""
    return float(string.replace(",", ""))


def insert_row(name: str, index: str, df: pd.DataFrame, row_value: List[str]):
    """Allows a row to be inserted after a given row in a pandas dataframe"""
    pd.options.mode.chained_assignment = None
    if name not in df.index:
        row_number = df.index.get_loc(index) + 1
        df1 = df[0:row_number]
        df2 = df[row_number:]
        df1.loc[name] = row_value
        df_result = pd.concat([df1, df2])
        return df_result
    return df


def set_cell(
    ws: worksheet,
    cell: str,
    text: opts = None,
    font: str = None,
    border: str = None,
    fill: str = None,
    alignment: str = None,
    num_form: str = None,
):
    """Sets the value of the cell to given text and formats based on specified arguments"""
    ws[cell] = text
    if font:
        ws[cell].font = font
    if border:
        ws[cell].border = border
    if fill:
        ws[cell].fill = fill
    if alignment:
        ws[cell].alignment = alignment
    if num_form:
        ws[cell].number_format = num_form


letters = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "AA",
    "AB",
    "AC",
    "AD",
    "AE",
    "AF",
    "AG",
    "AH",
    "AI",
    "AJ",
    "AK",
    "AL",
    "AM",
    "AN",
    "AO",
    "AP",
    "AQ",
    "AR",
    "AS",
    "AT",
    "AU",
    "AV",
    "AW",
    "AX",
    "AY",
    "AZ",
]
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

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    )
}

tickers = [
    "AEIS",
    "AEL",
    "AEM",
    "AEMD",
    "AENZ",
    "AEO",
    "AEP",
    "AER",
    "AERI",
    "AES",
]
