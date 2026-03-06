import yfinance as yf
import traceback

print("yfinance version:", yf.__version__)

try:
    df = yf.download(
        tickers="SPY",
        start="2024-01-01",
        end="2024-01-10",
        auto_adjust=False,
        progress=False,
        group_by="column",
        threads=False,
        timeout=10,
    )
    print("Success. Shape:", df.shape)
    print(df.head())
except Exception as e:
    print("Error:", e)
    traceback.print_exc()
