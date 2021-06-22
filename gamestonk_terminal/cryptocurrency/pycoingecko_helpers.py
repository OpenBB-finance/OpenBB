import datetime as dt
from datetime import timezone
from dateutil import parser
import json
import pandas as pd
import textwrap


def replace_underscores_to_newlines(cols: list, line: int = 13):
    """Helper method that replace underscores to white space and breaks it to new line

    Parameters
    ----------
    cols
        - list of columns names
    line
        - line length
    Returns
    -------
        list of column names with replaced underscores
    """
    return [
        textwrap.fill(c.replace("_", " "), line, break_long_words=False)
        for c in list(cols)
    ]


def find_discord(item: list) -> list or None:
    if isinstance(item, list) and len(item) > 0:
        discord = [chat for chat in item if "discord" in chat]
        if len(discord) > 0:
            return discord[0]


def join_list_elements(elem):
    if not elem:
        raise ValueError("Elem is empty")
    if isinstance(elem, dict):
        return ", ".join([k for k, v in elem.items()])
    elif isinstance(elem, list):
        return ", ".join([k for k in elem])
    else:
        return None


def filter_list(lst: list) -> list:
    if isinstance(lst, list) and len(lst) > 0:
        return [i for i in lst if i != ""]


def calculate_time_delta(date: str):
    now = dt.datetime.now(timezone.utc)
    if not isinstance(date, dt.datetime):
        date = parser.parse(date)
    return (now - date).days


def get_eth_addresses_for_cg_coins(file):  # pragma: no cover
    with open(file, "r") as f:
        data = json.load(f)
        df = pd.DataFrame(data)
        df["ethereum"] = df["platforms"].apply(
            lambda x: x.get("ethereum") if "ethereum" in x else None
        )
        return df


def clean_question_marks(dct: dict):
    if isinstance(dct, dict):
        for k, v in dct.items():
            if v == "?":
                dct[k] = None


def replace_qm(df):
    df.replace({"?": None, " ?": None}, inplace=True)
    return df


def get_url(url, elem):  # pragma: no cover
    return url + elem.find("a")["href"]


def clean_row(row):
    """Helper method that cleans whitespaces and newlines in text returned from BeautifulSoup
    Parameters
    ----------
    row
        text returned from BeautifulSoup find method
    Returns
    -------
        list of elements

    """
    return [r for r in row.text.strip().split("\n") if r not in ["", " "]]


def convert(word):
    return "".join(x.capitalize() or "_" for x in word.split("_") if word.isalpha())


def collateral_auditors_parse(args):  # pragma: no cover
    if args and args[0] == "N/A":
        collateral = args[1:]
        auditors = []
    else:
        n_elem = int(args[0])
        auditors = args[1 : n_elem + 1]
        collateral = args[n_elem + 1 :]

    return auditors, collateral


def swap_columns(df):
    cols = list(df.columns)
    cols = [cols[-1]] + cols[:-1]
    df = df[cols]
    return df


def changes_parser(changes):
    if isinstance(changes, list) and len(changes) < 3:
        for i in range(3 - len(changes)):
            changes.append(None)
    else:
        changes = [None for _ in range(3)]
    return changes


def remove_keys(entries, the_dict):
    for key in entries:
        if key in the_dict:
            del the_dict[key]


def rename_columns_in_dct(dct, mapper):
    return {mapper.get(k, v): v for k, v in dct.items()}


def create_dictionary_with_prefixes(
    columns: [list, tuple], dct: dict, constrains: [list, tuple] = None
):
    results = {}
    for column in columns:
        ath_data = dct.get(column)
        for element in ath_data:
            if constrains:
                if element in constrains:
                    results[f"{column}_" + element] = ath_data.get(element)
            else:
                results[f"{column}_" + element] = ath_data.get(element)
    return results


def wrap_text_in_df(df: pd.DataFrame, w=55):  # pragma: no cover
    """
    Parameters
    ----------
    df: pd.DataFrame
        Data Frame with some data
    w: int
        length of text in column after which text is wrapped into new line

    Returns
    -------

    """
    return df.applymap(
        lambda x: "\n".join(textwrap.wrap(x, width=w)) if isinstance(x, str) else x
    )
