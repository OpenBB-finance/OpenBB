.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.
    [Source: https://docs.llama.fi/api]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.ldapps(
    limit: int = 100,
    sortby: str = '',
    ascend: bool = False,
    description: bool = False,
    drop_chain: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit: *int*
        The number of dApps to display
    sortby: *str*
        Key by which to sort data
    ascend: *bool*
        Flag to sort data descending
    description: *bool*
        Flag to display description of protocol
    drop_chain: *bool*
        Whether to drop the chain column

    
* **Returns**

    pd.DataFrame
        Information about DeFi protocols
    