---
title: OpenBB Charting
sidebar_position: 1
description: This page introduces the optional openbb-charting extension.
keywords:
- explanation
- OpenBB Platform
- Python client
- Fast API
- getting started
- extensions
- charting
- view
- Plotly
- toolkits
- community
- Plotly
- OpenBBFigure
- PyWry
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="OpenBB Charting - Extensions | OpenBB Platform Docs" />

## Overview

The `openbb-charting` extension provides elements for building and displaying interactive charts, tables, dashboards, and more, directly from the OpenBB Platform's Python Interface and FAST API.

It allows users to create a custom view, without any previous experience working with Plotly, from any response served by the OpenBB Platform.

The Python Interface includes a custom [PyWry](https://github.com/OpenBB-finance/pywry) backend for displaying any content, in a WebKit HTML window served over `localhost`. In an IDE setting, they will be rendered inline.

To install, follow the instructions [here](installation). The sections below provide a general explanation of the extension.

## How Does It Work?

It works by extending the `OBBject` class with a new attribute, `charting`. When it is installed, every response from the OpenBB Platform will be equipped with these tools.

For functions that have pre-defined views, it serves as an intermediary between the user request and the response, activated when `chart=True`. When a chart is created, it will populate the existing, `chart`, attribute of the `OBBject`. This is where it is served by the FAST API from the function request. In the Python Interface, charts can be generated post-request, regardless of `chart=True`.

The `chart` attribute in the OBBject contains three items, responses from the API have two:

- `fig`: The OpenBBFigure object - an extended Plotly GraphObjects class. Not included in the API response.
- `content`: The Plotly JSON representation of the chart - Returned to the API.
- `format`: The format of the chart - 'plotly' is currently the only charting library.

There is one OBBject class method, `show()`, which will display the contents of the `chart` attribute, if populated.

The new `charting` attribute that binds to the OBBject also has a `show()` method.  This differs in that it overwrites the existing chart, effectively a 'reset' for the view.

The extension has a docstring, and it lists the class methods within `charting`.

```python
from openbb import obb
data = obb.equity.price.historical("AAPL")
data.charting?
```

```console
Charting extension.

Methods
-------
show
    Display chart and save it to the OBBject.
to_chart
    Redraw the chart and save it to the OBBject, with an optional entry point for Data.
functions
    Return a list of Platform commands with charting functions.
get_params
    Return the charting parameters for the function the OBBject was created from.
indicators
    Return the list of the available technical indicators to use with the `to_chart` method and OHLC+V data.
table
    Display an interactive table.
create_line_chart
    Create a line chart from external data.
create_bar_chart
    Create a bar chart, on a single x-axis with one or more values for the y-axis, from external data.
```

:::note
When creating a chart directly from the OpenBB Platform endpoint, chart parameters must be passed as a nested dictionary under the name, `chart_params`.

```python
chart_params = dict(
    title="AAPL 50/200 Day EMA",
    indicators=dict(
        ema=dict(length=[50,200]),
    ),
)
params = dict(
    symbol="AAPL",
    start_date="2022-01-01",
    provider="yfinance",
    chart=True,
    chart_params=chart_params,
)
data = obb.equity.price.historical(**params)
```

`chart_params` are sent in the body of the request when using the API.
:::

Passing only `chart=True` will return a default view which can be modified and drawn again post-request, via the `OBBject`.

```console
OBBject

id: 06614d74-7443-7201-8000-a65f358136a3
results: [{'date': datetime.date(2022, 1, 3), 'open': 177.8300018310547, 'high': 18...
provider: yfinance
warnings: None
chart: {'content': {'data': [{'close': [182.00999450683594, 179.6999969482422, 174....
extra: {'metadata': {'arguments': {'provider_choices': {'provider': 'yfinance'}, 's...
```

```python
data.show()
```

![candles with ema](https://github.com/OpenBB-finance/OpenBB/assets/85772166/b427d68b-777e-4230-852a-df749c5dbc46)

### No Render

The charts can be created without opening the PyWry window, and this is the default behaviour when `chart=True`.
With the `charting.show()` and `charting.to_chart()` methods, the default is `render=True`.
Setting as `False` will return the chart to itself, populating the `chart` attribute of OBBject.

## What Endpoints Have Charts?

The OpenBB Platform router, open_api.json, function signatures, and documentation are all generated based on your specific configuration. When the `openbb-charting` extension is installed, any function found in the "[charting_router](https://github.com/OpenBB-finance/OpenBB/blob/develop/openbb_platform/obbject_extensions/charting/openbb_charting/charting_router.py)" adds `chart: bool = False` to the command on build. For example, `obb.index.price.historical?`

```python
Signature:
obb.index.price.historical(
    symbol: Annotated[Union[str, List[str]], OpenBBCustomParameter(description='Symbol to get data for. Multiple comma separated items allowed for provider(s): cboe, fmp, intrinio, polygon, yfinance.')],
    ...
    chart: typing.Annotated[bool, OpenBBCustomParameter(description='Whether to create a chart or not, by default False.')] = False,
    **kwargs,
) -> openbb_core.app.model.obbject.OBBject
```

### Charting Functions

The `charting` attribute of every command output has methods for identifying the charting functions and parameters.
While able to serve JSON-serializable charts, the `openbb-charting` extension is best-suited for use with the Python Interface. Much of the functionality is realized post-request.

Examine the extension by returning any command at all.

```python
from openbb import obb

data = obb.equity.price.historical("SPY,QQQ,XLK,BTC-USD", provider="yfinance")

data.charting.functions()
```

```console
['crypto_price_historical',
 'currency_price_historical',
 'economy_fred_series',
 'equity_price_historical',
 'equity_price_performance',
 'etf_historical',
 'etf_holdings',
 'etf_price_performance',
 'index_price_historical',
 'technical_adx',
 'technical_aroon',
 'technical_cones',
 'technical_ema',
 'technical_hma',
 'technical_macd',
 'technical_rsi',
 'technical_sma',
 'technical_wma',
 'technical_zlma']
```

:::tip
The list above should, as shown here, should not be considered as the source of truth. It's just a sample.
:::

If the `OBBject` in question has a dedicated charting function associated with it, parameters are detailed by the `get_params()` method.

```console
EquityPriceHistoricalChartQueryParams

    Parameters
    ----------

    data : Union[Data, list[Data], NoneType]
        Filtered versions of the data contained in the original `self.results`.
        Columns should be the same as the original data.
        Example use is to reduce the number of columns, or the length of data, to plot.

    title : Union[str, NoneType]
        Title of the chart.

    target : Union[str, NoneType]
        The specific column to target.
        If supplied, this will override the candles and volume parameters.

    multi_symbol : bool
        Flag to indicate whether the data contains multiple symbols.
        This is mostly handled automatically, but if the chart fails to generate try setting this to True.

    same_axis : bool
        If True, forces all data to be plotted on the same axis.

    normalize : bool
        If True, the data will be normalized and placed on the same axis.

    returns : bool
        If True, the cumulative returns for the length of the time series will be calculated and plotted.

    candles : bool
        If True, and OHLC exists, and there is only one symbol in the data, candles will be plotted.

    heikin_ashi : bool
        If True, and `candles=True`, Heikin Ashi candles will be plotted.

    volume : bool
        If True, and volume exists, and `candles=True`, volume will be plotted.

    indicators : Union[ChartIndicators, dict[str, dict[str, Any]], NoneType]
        Indicators to be plotted, formatted as a dictionary.
        Data containing multiple symbols will ignore indicators.
        Example:
            indicators = dict(
                sma=dict(length=[20,30,50]),
                adx=dict(length=14),
                rsi=dict(length=14),
            )
```

Not all commands will have the same `chart_params`, and some less than others, but it is always possible to redraw the chart with a different combination post-request. Here's what the default chart is from the output of the command above.

If `chart=True` was not specified, it will need to be created.

```python
data.charting.to_chart()
```

![obb.equity.price.historical()](https://github.com/OpenBB-finance/OpenBB/assets/85772166/9231c455-ee1b-47a8-a627-b0034ea52ecd)

The extension recognized that multiple symbols were within the object, and made a determination to display cumulative returns by default.

A candlestick chart will draw only when there is one symbol in the data.

```python
obb.equity.price.historical(
    symbol="XLK",
    start_date="2024-01-01",
    provider="yfinance",
    chart=True,
    chart_params=dict(title="XLK YTD", heikin_ashi=True)
).show()
```

![obb.equity.price.historical()](https://github.com/OpenBB-finance/OpenBB/assets/85772166/13af30b3-7298-402d-ac32-1f7700cd08fd)

## Endpoints Without Charts

Most functions do not have dedicated charts. However, it's still possible to generate one automatically. Using the `data` above, we can try passing it through a quantitative analysis command.

```python
data = obb.equity.price.historical(
    symbol="XLK",
    start_date="2023-01-01",
    provider="yfinance",
)
qa = obb.quantitative.rolling.stdev(data.results, target="close")

qa.charting.show(title="XLK Rolling 21 Day Standard Deviation")
```

![auto chart](https://github.com/OpenBB-finance/OpenBB/assets/85772166/f87a6648-7365-4529-a254-35897af448ca)

## Charts From Any Data

There are methods for creating a generic chart from any external data.
They will bypass any data contained in the parent object, unless specifically fed into itself.

- charting.create_bar_chart()
- charting.create_line_chart()

They can also be used as standalone components by initializing an empty instance of the OBBject class.

```python
from openbb import obb
from openbb_core.app.model.obbject import OBBject
create_bar_chart = OBBject(results=None).charting.create_bar_chart

create_bar_chart?
````

```console
Create a bar chart on a single x-axis with one or more values for the y-axis.

Parameters
----------
data : Union[list, dict, pd.DataFrame, List[pd.DataFrame], pd.Series, List[pd.Series], np.ndarray, Data]
    Data to plot.
x : str
    The x-axis column name.
y : Union[str, List[str]]
    The y-axis column name(s).
barmode : Literal["group", "stack", "relative", "overlay"], optional
    The bar mode, by default "group".
xtype : Literal["category", "multicategory", "date", "log", "linear"], optional
    The x-axis type, by default "category".
title : Optional[str], optional
    The title of the chart, by default None.
xtitle : Optional[str], optional
    The x-axis title, by default None.
ytitle : Optional[str], optional
    The y-axis title, by default None.
orientation : Literal["h", "v"], optional
    The orientation of the chart, by default "v".
colors: Optional[List[str]], optional
    Manually set the colors to cycle through for each column in 'y', by default None.
layout_kwargs : Optional[Dict[str, Any]], optional
    Additional keyword arguments to apply with figure.update_layout(), by default None.

Returns
-------
OpenBBFigure
    The OpenBBFigure object.
```

## Tables

The `openbb-charting` extension is equipped with interactive tables, utilizing the React framework. They are displayed by using the `table` method.

```python
data = obb.equity.price.quote("AAPL,MSFT,GOOGL,META,TSLA,AMZN", provider="yfinance")
data.charting.table()
```

![Interactive Tables](https://github.com/OpenBB-finance/OpenBB/assets/85772166/77f5f812-b933-4ced-929c-c1e39b2a3eed)

External data can also be supplied, providing an opportunity to filter or apply Pandas operations before display.

```python
new_df = df.to_df().T
new_df.index.name="metric"
new_df.columns = new_df.loc["symbol"]
new_df.drop("symbol", inplace=True)
data.charting.table(data=new_df)
```

![Tables From External Data](https://github.com/OpenBB-finance/OpenBB/assets/85772166/d02f8c34-e1d1-4001-a73e-d3b948a4c5c1)

:::important
This does not alter the contents of the original object, the displayed data is a copy.
:::
