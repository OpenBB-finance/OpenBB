import yfinance as yf

for auto_adj in [True, False]:
    for gb in ["column", "ticker"]:
        print(f"\n--- auto_adjust={auto_adj}, group_by={gb} ---")
        try:
            df = yf.download(
                tickers="SPY",
                start="2024-01-01",
                end="2024-01-10",
                auto_adjust=auto_adj,
                progress=False,
                group_by=gb,
                threads=False,
                timeout=10,
            )
            print("Shape:", df.shape)
            if not df.empty:
                print("First row Date:", df.index[0])
        except Exception as e:
            print("Error:", e)
