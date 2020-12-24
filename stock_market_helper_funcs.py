
from pytz import timezone
from holidays import US as holidaysUS
from datetime import datetime, time as Time
import matplotlib
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------------------------------------------------
def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return ivalue


# -----------------------------------------------------------------------------------------------------------------------
def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError("Not a valid date: {s}")


# -----------------------------------------------------------------------------------------------------------------------
def plot_view_stock(df, symbol):
    pfig, axVolume = plt.subplots()
    plt.bar(df.index, df['5. volume'].values, color='k', alpha=0.8)
    plt.ylabel('Volume')
    axPrice = axVolume.twinx()
    plt.plot(df.index, df.iloc[:, :-1])
    plt.title(symbol + ' (Time Series)')
    plt.xlim(df.index[0], df.index[-1])
    plt.xlabel('Time')
    plt.ylabel('Share Price ($)')
    plt.legend(df.columns)
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.show()


# -----------------------------------------------------------------------------------------------------------------------
def plot_stock_ta(df_stock, s_stock, df_ta, s_ta):
    plt.plot(df_stock.index, df_stock.values)
    plt.plot(df_ta.index, df_ta.values)
    plt.title(f"{s_ta} on {s_stock}")
    plt.xlim(df_stock.index[0], df_stock.index[-1])
    plt.xlabel('Time')
    plt.ylabel('Share Price ($)')
    plt.legend([s_stock, s_ta])
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.show()
    print("")


# -----------------------------------------------------------------------------------------------------------------------
def b_is_stock_market_open():
    ''' checks if the stock market is open '''
    # Get current US time
    now = datetime.now(timezone('US/Eastern'))
    # Check if it is a weekend
    if now.date().weekday() > 4:
        return False
    # Check if it is a holiday
    if now.strftime('%Y-%m-%d') in holidaysUS():
        return False
    # Check if it hasn't open already
    if now.time() < Time(hour=9, minute=30, second=0):
        return False
    # Check if it has already closed
    if now.time() > Time(hour=16, minute=0, second=0):
        return False
    # Otherwise, Stock Market is open!
    return True

