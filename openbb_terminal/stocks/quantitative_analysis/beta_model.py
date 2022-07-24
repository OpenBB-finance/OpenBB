from scipy import stats
from openbb_terminal.stocks import stocks_helper


def process_beta(stock_ticker, ref_ticker, stock=None, ref=None):
    """Calculate beta for a ticker and a reference ticker.

    Parameters
    ----------
    stock_ticker : string
    ref_ticker : string
    stock : pd.DataFrame
        A df of price data for stock_ticker with column 'Close'
    ref : pd.DataFrame
        A df of price data for ref_ticker with column 'Close'

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
        stock = stock.rename()
    else:
        # TODO: When loaded in the stocks menu, the stock df columns are all
        # lowercase but when loaded via stocks_helper.load(ticker) they start
        # with an uppercase char. This should be consistent.
        stock = stock.rename({"close": "Close"}, axis=1)
    if ref is None:
        ref = stocks_helper.load(ref_ticker)
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
