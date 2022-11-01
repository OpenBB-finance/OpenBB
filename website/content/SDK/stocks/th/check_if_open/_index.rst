.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Check if market open helper function
    </h3>

{{< highlight python >}}
stocks.th.check_if_open(
    bursa: pandas.core.frame.DataFrame,
    exchange: str
) -> bool
{{< /highlight >}}

* **Parameters**

    bursa : *pd.DataFrame*
        pd.DataFrame of all exchanges
    exchange : *str*
        bursa pd.DataFrame index value for exchange

    
* **Returns**

    bool
        If market is open
    