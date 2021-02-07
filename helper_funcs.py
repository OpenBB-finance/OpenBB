
from pytz import timezone
from holidays import US as holidaysUS
from datetime import datetime, time as Time
import sys
import matplotlib
import matplotlib.pyplot as plt
from datetime import timedelta
from pytz import timezone
from holidays import US as holidaysUS
from datetime import datetime, timedelta, time as Time

# -----------------------------------------------------------------------------------------------------------------------
def check_non_negative(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(f"{value} is negative")
    return ivalue


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
    plt.bar(df.index, df.iloc[:, -1], color='k', alpha=0.8, width=.3)
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
    print("")


# -----------------------------------------------------------------------------------------------------------------------
def plot_stock_ta(df_stock, s_ticker, df_ta, s_ta):
    plt.plot(df_stock.index, df_stock.values, color='k')
    plt.plot(df_ta.index, df_ta.values)
    plt.title(f"{s_ta} on {s_ticker}")
    plt.xlim(df_stock.index[0], df_stock.index[-1])
    plt.xlabel('Time')
    plt.ylabel('Share Price ($)')
    # Pandas series
    if len(df_ta.shape) == 1:
        l_legend = [s_ticker, s_ta]
    # Pandas dataframe
    else:
        l_legend = df_ta.columns.tolist()
        l_legend.insert(0, s_ticker)
    plt.legend(l_legend)
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.show()
    print("")


# -----------------------------------------------------------------------------------------------------------------------
def plot_stock_and_ta(df_stock, s_ticker, df_ta, s_ta):
    pfig, axPrice = plt.subplots()
    plt.title(f"{s_ta} on {s_ticker}")
    plt.plot(df_stock.index, df_stock.values, 'k', lw=3)
    plt.xlim(df_stock.index[0], df_stock.index[-1])
    plt.xlabel('Time')
    plt.ylabel(f'Share Price of {s_ticker} ($)')
    axTa = axPrice.twinx()
    plt.plot(df_ta.index, df_ta.values)
    # Pandas series
    if len(df_ta.shape) == 1:
        l_legend = [s_ta]
    # Pandas dataframe
    else:
        l_legend = df_ta.columns.tolist()
    plt.legend(l_legend)
    axTa.set_ylabel(s_ta, color="tab:blue")
    axTa.spines['right'].set_color("tab:blue")
    axTa.tick_params(axis='y', colors="tab:blue")
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.show()
    print("")


# -----------------------------------------------------------------------------------------------------------------------
def plot_ta(s_ticker, df_ta, s_ta):
    plt.plot(df_ta.index, df_ta.values)
    plt.title(f"{s_ta} on {s_ticker}")
    plt.xlim(df_ta.index[0], df_ta.index[-1])
    plt.xlabel('Time')
    #plt.ylabel('Share Price ($)')
    #if isinstance(df_ta, pd.DataFrame):
    #    plt.legend(df_ta.columns)
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


# -----------------------------------------------------------------------------------------------------------------------
def long_number_format(num):
    if isinstance(num, float):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0 
        if num.is_integer():
            return '%d%s' % (num, ['', ' K', ' M', ' B', ' T', ' P'][magnitude])
        else:
            return '%.3f%s' % (num, ['', ' K', ' M', ' B', ' T', ' P'][magnitude]) 
    if isinstance(num, int):
        num = str(num)
    if num.lstrip("-").isdigit():
        num = int(num)
        num /= 1.0
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0 
        if num.is_integer():
            return '%d%s' % (num, ['', ' K', ' M', ' B', ' T', ' P'][magnitude])
        else:
            return '%.3f%s' % (num, ['', ' K', ' M', ' B', ' T', ' P'][magnitude])            
    return num


# -----------------------------------------------------------------------------------------------------------------------
def clean_data_values_to_float(val):
    # Remove parenthesis if they exist
    if val.startswith('('):
        val = val[1:]
    if val.endswith(')'):
        val = val[:-1]
        
    if val == '-':
        val = '0'
    
    # Convert percentage to decimal
    if val.endswith('%'):
        val = float(val[:-1])/100.0
    # Convert from billions
    elif val.endswith('B'):
        val = float(val[:-1])*1_000_000_000
    # Convert from millions
    elif val.endswith('M'):
        val = float(val[:-1])*1_000_000
    # Convert from thousands
    elif val.endswith('K'):
        val = float(val[:-1])*1_000
    else:
        val = float(val)

    return val


# -----------------------------------------------------------------------------------------------------------------------
def int_or_round_float(x):
    if (x - int(x) < -sys.float_info.epsilon) or (x - int(x) > sys.float_info.epsilon):
        return ' ' + str(round(x, 2))
    else:
        return ' ' + str(int(x))


# -----------------------------------------------------------------------------------------------------------------------
def divide_chunks(l, n):   
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n]


# -----------------------------------------------------------------------------------------------------------------------
def get_next_stock_market_days(last_stock_day, n_next_days):
    n_days = 0
    l_pred_days = list()
    while n_days < n_next_days:

        last_stock_day += timedelta(hours=24)

        # Check if it is a weekend
        if last_stock_day.date().weekday() > 4:
            continue
        # Check if it is a holiday
        if last_stock_day.strftime('%Y-%m-%d') in holidaysUS():
            continue
        # Otherwise stock market is open
        else:
            n_days += 1
            l_pred_days.append(last_stock_day)
            
    return l_pred_days
