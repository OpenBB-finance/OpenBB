.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.defi.sinfo(
    address: str = '',
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

.. raw:: html

    <p>
    Get staking info for provided terra account [Source: https://fcd.terra.dev/swagger]
    </p>

* **Parameters**

    address: str
        terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg
    chart: bool
       Flag to display chart


* **Returns**

    Tuple[pd.DataFrame, str]:
        luna delegations and summary report for given address

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.sinfo(
    address: str = '',
    limit: int = 10,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]
    </p>

* **Parameters**

    address: str
        terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg
    limit: int
        Number of records to display
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

