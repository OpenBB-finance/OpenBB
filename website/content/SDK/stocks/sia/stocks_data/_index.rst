.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.sia.stocks_data(
    symbols: List[str] = None,
    finance_key: str = 'ncf',
    stocks_data: dict = None,
    period: str = 'annual',
    symbol: str = 'USD',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get stocks data based on a list of stocks and the finance key. The function searches for the
    correct financial statement automatically. [Source: StockAnalysis]
    </p>

* **Parameters**

    symbols: list
        A list of tickers that will be used to collect data for.
    finance_key: str
        The finance key used to search within the SA_KEYS for the correct name of item
        on the financial statement
    stocks_data : dict
        A dictionary that is empty on initialisation but filled once data is collected
        for the first time.
    period : str
        Whether you want annually, quarterly or trailing financial statements.
    symbol : str
        Choose in what currency you wish to convert each company's financial statement.
        Default is USD (US Dollars).

* **Returns**

    dict
        Dictionary of filtered stocks data separated by financial statement
