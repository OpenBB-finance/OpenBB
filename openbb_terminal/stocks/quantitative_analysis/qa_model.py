import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None


def full_stock_df(df: pd.DataFrame) -> pd.DataFrame:
    df["Returns"] = df["Adj Close"].pct_change()
    df["LogRet"] = np.log(df["Adj Close"]) - np.log(df["Adj Close"].shift(1))
    df["LogPrice"] = np.log(df["Adj Close"])
    df = df.rename(columns={"Adj Close": "AdjClose"})
    df = df.dropna()
    df.columns = [x.lower() for x in df.columns]
    return df
