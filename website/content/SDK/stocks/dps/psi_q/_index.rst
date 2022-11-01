.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Plots the short interest of a stock. This corresponds to the
    number of shares that have been sold short but have not yet been
    covered or closed out. Either NASDAQ or NYSE [Source: Quandl]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
stocks.dps.psi_q(
    symbol: str,
    nyse: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        ticker to get short interest from
    nyse : *bool*
        data from NYSE if true, otherwise NASDAQ

    
* **Returns**

    pd.DataFrame
        short interest volume data
    