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
crypto.dd.tk(
    symbol: str,
    coingecko_id: str,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

.. raw:: html

    <p>
    Returns coin tokenomics
    [Source: https://messari.io/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check tokenomics
    coingecko_id : str
        ID from coingecko
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Metric Value tokenomics
    pd.DataFrame
        Circulating supply overtime

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.tk(
    symbol: str,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display coin tokenomics
    [Source: https://messari.io/]
    </p>

* **Parameters**

    symbol : str
        Crypto symbol to check tokenomics
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    chart: bool
       Flag to display chart

