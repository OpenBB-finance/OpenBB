.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get staking info for provided terra account [Source: https://fcd.terra.dev/swagger]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.sinfo(
    address: str = '',
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

* **Parameters**

    address: *str*
        terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg
    
* **Returns**

    Tuple[pd.DataFrame, str]:
        luna delegations and summary report for given address
   