import textwrap
import pandas as pd


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


def percent_to_float(s: str):
    """Helper method to replace string pct like "123.56%" to float 1.2356
    Parameters
    ----------
    s: string
        string to replace
    Returns
    -------
    float
    """
    s = str(float(s.rstrip("%")))
    i = s.find(".")
    if i == -1:
        return int(s) / 100
    if s.startswith("-"):
        return -percent_to_float(s.lstrip("-"))
    s = s.replace(".", "")
    i -= 2
    if i < 0:
        return float("." + "0" * abs(i) + s)
    return float(s[:i] + "." + s[i:])


def create_df_index(df: pd.DataFrame, name="rank"):
    df.index = df.index + 1
    df.reset_index(inplace=True)
    df.rename(columns={"index": name}, inplace=True)
