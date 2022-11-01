.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Display top dApps (in terms of TVL) grouped by chain.
    [Source: https://docs.llama.fi/api]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.gdapps(
    limit: int = 50,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit: *int*
        Number of top dApps to display

    
* **Returns**

    pd.DataFrame
        Information about DeFi protocols grouped by chain
    