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
crypto.dd.headlines(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]
    </p>

* **Parameters**

    symbol : str
        Ticker symbol to get the sentiment analysis from
    chart: bool
       Flag to display chart


* **Returns**

    DataFrame()
        Empty if there was an issue with data retrieval

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.headlines(
    symbol: str,
    raw: bool = False,
    export: str = '',
    external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Sentiment analysis from FinBrain for Cryptocurrencies

    FinBrain collects the news headlines from 15+ major financial news
    sources on a daily basis and analyzes them to generate sentiment scores
    for more than 4500 US stocks. FinBrain Technologies develops deep learning
    algorithms for financial analysis and prediction, which currently serves
    traders from more than 150 countries all around the world.
    [Source:  https://finbrain.tech]
    </p>

* **Parameters**

    symbol: str
        Cryptocurrency
    raw : False
        Display raw table data
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    chart: bool
       Flag to display chart

