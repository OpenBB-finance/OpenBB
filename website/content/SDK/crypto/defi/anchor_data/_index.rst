.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns anchor protocol earnings data of a certain terra address
    [Source: https://cryptosaurio.com/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.anchor_data(
    address: str = '',
    chart: bool = False
) -> Tuple[Any, Any, str]
{{< /highlight >}}

* **Parameters**

    address : *str*
        Terra address. Valid terra addresses start with 'terra'
    
* **Returns**

    Tuple:
        - pandas.DataFrame: *Earnings over time in UST*
        - pandas.DataFrame: *History of transactions*
        - str: *             Overall statistics*
    