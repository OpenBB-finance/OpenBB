from scipy import stats
from openbb_terminal.stocks import stocks_helper


def process_beta(stock_ticker, ref_ticker):
    stock = stocks_helper.load(stock_ticker)
    ref = stocks_helper.load(ref_ticker)
    sr = 100 * stock["Close"].pct_change().to_frame()
    sr = sr.rename({"Close": "Stock Pct Ret"}, axis=1)
    rr = 100 * ref["Close"].pct_change().to_frame()
    rr = rr.rename({"Close": "Ref Pct Ret"}, axis=1)
    df = sr.merge(rr, how="outer", left_index=True, right_index=True)
    df = df.dropna()
    sr = df["Stock Pct Ret"].tolist()
    rr = df["Ref Pct Ret"].tolist()
    model = stats.linregress(rr, sr)
    beta = model.slope
    alpha = model.intercept
    return sr, rr, beta, alpha
