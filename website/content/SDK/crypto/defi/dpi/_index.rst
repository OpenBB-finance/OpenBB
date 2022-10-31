.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Scrapes data from DeFi Pulse with all DeFi Pulse crypto protocols.
    [Source: https://defipulse.com/]

    Returns
    -------
    pd.DataFrame
        List of DeFi Pulse protocols.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.dpi(
    sortby: str = 'TVL_$', ascend: bool = False,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

lse with all DeFi Pulse crypto protocols.
    [Source: https://defipulse.com/]

    
* **Returns**

    pd.DataFrame
        List of DeFi Pulse protocols.
    