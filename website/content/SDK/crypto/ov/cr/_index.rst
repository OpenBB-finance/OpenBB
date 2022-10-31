.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns crypto {borrow,supply} interest rates for cryptocurrencies across several platforms
    [Source: https://loanscan.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.cr(
    rate\_type: str = 'borrow',
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    rate_type : *str*
        Interest rate type: {borrow, supply}. Default: *supply*
    
* **Returns**

    pandas.DataFrame: *crypto interest rates per platform*
    