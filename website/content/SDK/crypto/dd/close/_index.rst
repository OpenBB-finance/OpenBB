.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns the price of a cryptocurrency
    [Source: https://glassnode.com]
    </h3>

{{< highlight python >}}
crypto.dd.close(
    symbol: str,
    start_date: str = '2010-01-01', end_date: str = '2022-11-01', print_errors: bool = True,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto to check close price (BTC or ETH)
    start_date : *str*
        Initial date, format YYYY-MM-DD
    end_date : *str*
        Final date, format YYYY-MM-DD
    print_errors: *bool*
        Flag to print errors. Default: *True*

    
* **Returns**

    pd.DataFrame
        price over time
    