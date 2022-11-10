.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.chart(
    prices_df: 'pd.DataFrame',
    to_symbol: 'str' = '',
    from_symbol: 'str' = '',
    source: 'str' = '',
    exchange: 'str' = '',
    interval: 'str' = '',
    external_axes: 'list[plt.Axes] | None' = None, yscale: 'str' = 'linear',
    chart: bool = False,
) -> 'None'
{{< /highlight >}}

.. raw:: html

    <p>
    Load data for Technical Analysis
    </p>

* **Parameters**

    prices_df: pd.DataFrame
        Cryptocurrency
    to_symbol: str
        Coin (only used for chart title), by default ""
    from_symbol: str
        Currency (only used for chart title), by default ""
    yscale: str
        Scale for y axis of plot Either linear or log
    chart: bool
       Flag to display chart


|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.chart(
    prices_df: 'pd.DataFrame',
    to_symbol: 'str' = '',
    from_symbol: 'str' = '',
    source: 'str' = '',
    exchange: 'str' = '',
    interval: 'str' = '',
    external_axes: 'list[plt.Axes] | None' = None, yscale: 'str' = 'linear',
    chart: bool = False,
) -> 'None'
{{< /highlight >}}

.. raw:: html

    <p>
    Load data for Technical Analysis
    </p>

* **Parameters**

    prices_df: pd.DataFrame
        Cryptocurrency
    to_symbol: str
        Coin (only used for chart title), by default ""
    from_symbol: str
        Currency (only used for chart title), by default ""
    yscale: str
        Scale for y axis of plot Either linear or log
    chart: bool
       Flag to display chart

