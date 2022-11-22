.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.dd.close(
    symbol: str,
    start_date: str = '2010-01-01',
    end_date: str = None,
    print_errors: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns the price of a cryptocurrency
    [Source: https://glassnode.com]
    </p>

* **Parameters**

    symbol : str
        Crypto to check close price (BTC or ETH)
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : str
        Final date, format YYYY-MM-DD
    print_errors: bool
        Flag to print errors. Default: True

* **Returns**

    pd.DataFrame
        price over time
