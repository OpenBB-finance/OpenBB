.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.gov.government_trading(
    gov_type: str = 'congress',
    symbol: str = '',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns the most recent transactions by members of government
    </p>

* **Parameters**

    gov_type: str
        Type of government data between:
        'congress', 'senate', 'house', 'contracts', 'quarter-contracts' and 'corporate-lobbying'
    symbol : str
        Ticker symbol to get congress trading data from

* **Returns**

    pd.DataFrame
        Most recent transactions by members of U.S. Congress
