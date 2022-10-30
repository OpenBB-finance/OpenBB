.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get the last 100 swaps done on Uniswap [Source: https://thegraph.com/en/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.swaps(
    limit: int = 100,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit: *int*
        Number of swaps to return. Maximum possible number: *1000.*
    
* **Returns**

    pd.DataFrame
        Last 100 swaps on Uniswap
    