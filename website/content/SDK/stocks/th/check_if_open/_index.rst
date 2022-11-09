.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.th.check_if_open(
    bursa: pandas.core.frame.DataFrame,
    exchange: str,
    chart: bool = False,
) -> bool
{{< /highlight >}}

.. raw:: html

    <p>
    Check if market open helper function
    </p>

* **Parameters**

    bursa : pd.DataFrame
        pd.DataFrame of all exchanges
    exchange : str
        bursa pd.DataFrame index value for exchange

* **Returns**

    bool
        If market is open
