.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns information about historical tvl of a defi protocol.
    [Source: https://docs.llama.fi/api]

    Returns
    -------
    pd.DataFrame
        Historical tvl
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.dtvl(
    protocol: str,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

 historical tvl of a defi protocol.
    [Source: https://docs.llama.fi/api]

    
* **Returns**

    pd.DataFrame
        Historical tvl
    