.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns historical data of an asset in a certain terra address
    [Source: https://terra.engineer/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.aterra(
    asset: str = 'ust',
    address: str = 'terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    asset : *str*
        Terra asset {ust,luna,sdt}
    address : *str*
        Terra address. Valid terra addresses start with 'terra'
    
* **Returns**

    pd.DataFrame
        historical data
    