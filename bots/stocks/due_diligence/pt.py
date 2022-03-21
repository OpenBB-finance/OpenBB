import io
import logging
from datetime import datetime, timedelta

from matplotlib import pyplot as plt

from bots import imps
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.due_diligence import business_insider_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def pt_command(ticker: str = "", raw: bool = False, start=""):
    """Displays price targets [Business Insider]"""

    # Debug
    if imps.DEBUG:
        logger.debug("dd pt %s", ticker)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    if start == "":
        start = datetime.now() - timedelta(days=365)
    else:
        start = datetime.strptime(start, imps.DATE_FORMAT)

    if raw not in [True, False]:
        raise Exception("raw argument has to be true or false")

    df_analyst_data = business_insider_model.get_price_target_from_analysts(ticker)
    stock = imps.load(ticker, start)
    title = f"Stocks: [Business Insider] Price Targets {ticker}"
    if df_analyst_data.empty or stock.empty:
        raise Exception("Enter valid ticker")

    # Output Data

    if raw:
        df_analyst_data.sort_index(ascending=False)
        report = "```" + df_analyst_data.to_string() + "```"

        output = {
            "title": title,
            "description": report,
        }
    else:
        plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        if start:
            df_analyst_data = df_analyst_data[start:]

        plt.plot(stock.index, stock["Adj Close"].values, lw=3)

        plt.plot(df_analyst_data.groupby(by=["Date"]).mean())

        plt.scatter(df_analyst_data.index, df_analyst_data["Price Target"], c="r", s=40)

        plt.legend(["Closing Price", "Average Price Target", "Price Target"])

        plt.title(f"{ticker.upper()} (Time Series) and Price Target")
        plt.xlim(stock.index[0], stock.index[-1])
        plt.xlabel("Time")
        plt.ylabel("Share Price")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        imagefile = "ta_pt.png"
        dataBytesIO = io.BytesIO()
        plt.savefig(dataBytesIO)
        plt.close("all")

        dataBytesIO.seek(0)
        imagefile = imps.image_border(imagefile, base64=dataBytesIO)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
