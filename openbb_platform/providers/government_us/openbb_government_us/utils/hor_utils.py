import re
from PyPDF2 import PdfReader
from typing import Any, Dict

"""
Utility  methods to extract data from pdf rows
"""


def extract_from_disclosure(pdf_reader: PdfReader) -> dict[str, Any]:
    holder = {}
    # page 0 has all information about the HOR Member
    start_token = "SP"  # START token
    # then we have two blanks
    # then we have ticker [ST] Transaction Transaction Date Amount #

    filer_info: Dict[str, int] = {}
    for page_num in range(0, len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]

        text = page.extract_text()
        transactions = text
        rowHolder = []
        rows = transactions.splitlines()
        seen = False
        transaction_holder = []
        # need to read line by line, considering only rows that start with 'SP'

        for row in rows:
            row = row.encode("utf-8").decode("utf-8")
            if row.startswith(start_token):
                seen = not seen
            if seen:
                if row:
                    if (
                        row.find("\x00") < 0
                    ):  # row with this character are 'intermediate' row
                        transaction_holder.append(row)
                    else:
                        seen = False
                        rowHolder.append(" ".join(transaction_holder))
                        transaction_holder = []
        holder[page_num] = rowHolder
    return {"info": filer_info, "transactions": holder}


def extract_data(first_row: str) -> dict[str, Any]:
    # Here we try to extract item from each row
    # regex did not work well, as some time there were '\x0' characters
    # so doing a brute force check
    # pylint: disable=no-member
    ticker_idx_st = first_row.find("(")

    if ticker_idx_st < 0:
        ticker = "N/A"
        company_name = first_row[0 : first_row.find("[")]
    else:
        ticker_idx_end = first_row.index(")")
        ticker = first_row[ticker_idx_st + 1 : ticker_idx_end]
        company_name = first_row[0:ticker_idx_st]

    if first_row.find("[") < 0:
        action = "N/A"
        purchase_price = "N/A"
    else:
        action_idx = first_row.index("[") + 4
        purchase_idx = first_row.index("$")
        action = first_row[action_idx : action_idx + 2]
        purchase_price = first_row[purchase_idx:]

    pattern = r"\d{2}/\d{2}/\d{4}"
    matches = re.findall(pattern, first_row)

    # Extract the two dates from the matches
    dates = matches
    if dates:
        date1 = dates[0]
        date2 = dates[1] if len(dates) > 1 else "N/A"
    else:
        date1 = "N/A"
        date2 = "N/A"

    # need to add filer info
    data = dict(
        company=company_name,
        ticker=ticker,
        action=action,
        purchase_price=purchase_price,
        transaction_date=date1,
        report_date=date2,
    )
    return data


def extract_transactions(holder_dict, member_dict):
    row_list = []
    for page_num, lst in holder_dict.items():
        for row in lst:
            row = extract_data(row)
            row.update(member_dict)
            row_list.append(row)
    return row_list
