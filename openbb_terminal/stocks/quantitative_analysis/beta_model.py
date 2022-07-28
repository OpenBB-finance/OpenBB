import pandas as pd
from scipy import stats
from openbb_terminal.stocks import stocks_helper


def beta_model(
    stock_ticker: str,
    ref_ticker: str,
    stock: pd.DataFrame = None,
    ref: pd.DataFrame = None,
) -> tuple[pd.Series, pd.Series, float, float]:
    """Calculate beta for a ticker and a reference ticker.

    Parameters
    ----------
    stock_ticker : str
        A ticker to calculate beta for
    ref_ticker : str
        A reference ticker for the beta calculation (default in terminal is SPY)
    stock : pd.DataFrame
        stock_ticker price data
    ref : pd.DataFrame
        ref_ticker price data

    Returns
    -------
    sr : pd.Series
        stock_ticker close-to-close returns
    rr : pd.Series
        ref_ticker close-to-close returns
    beta : float
    alpha : float
    """
    if stock is None:
        stock = stocks_helper.load(stock_ticker)
    else:
        # TODO: When loaded in the stocks menu, the stock df columns are all
        # lowercase but when loaded via stocks_helper.load(ticker) they start
        # with an uppercase char. This should be consistent.
        stock = stock.rename({"close": "Close"}, axis=1)
    if ref is None:
        ref = stocks_helper.load(ref_ticker)
        if ref.empty:
            raise Exception("Invalid ref ticker")
    else:
        ref = ref.rename({"close": "Close"}, axis=1)

    # join returns
    sr = 100 * stock["Close"].pct_change().to_frame()
    sr = sr.rename({"Close": "Stock Pct Ret"}, axis=1)
    rr = 100 * ref["Close"].pct_change().to_frame()
    rr = rr.rename({"Close": "Ref Pct Ret"}, axis=1)
    df = sr.merge(rr, how="outer", left_index=True, right_index=True)
    df = df.dropna()
    sr = df["Stock Pct Ret"].tolist()
    rr = df["Ref Pct Ret"].tolist()

    # compute lin reg
    model = stats.linregress(rr, sr)
    beta = model.slope
    alpha = model.intercept

    return sr, rr, beta, alpha
