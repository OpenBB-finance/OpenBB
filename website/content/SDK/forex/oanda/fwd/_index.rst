.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets forward rates from fxempire
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
forex.oanda.fwd(
    to_symbol: str = 'USD',
    from_symbol: str = 'EUR',
    chart: bool = False,
)
{{< /highlight >}}

* **Parameters**

    to_symbol: *str*
        To currency
    from_symbol: *str*
        From currency

    
* **Returns**

    df: *pd.DataFrame*

   