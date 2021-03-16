import yfinance as yf
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


def get_volume_graph(ticker_name, exp_date):

    opt = yf.Ticker(ticker_name).option_chain(exp_date)
    # data available via: opt.calls, opt.puts

    volume_data = pd.concat(
        [
            __volume_data(opt.calls, 'calls'),
            __volume_data(opt.puts, 'puts')
        ],
        axis=0
    )
    fig = px.line(
        volume_data,
        x="strike",
        y="volume",
        title=f'{ticker_name} Volume for {exp_date}',
        color='type'
    )
    fig.show()


def __volume_data(opt_data, flag):
    # get option chain for specific expiration
    df = opt_data.pivot_table(
        index='strike',
        values=['volume', 'openInterest'],
        aggfunc='sum')
    df.reindex()
    df['strike'] = df.index
    df['type'] = flag
    return df
