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
crypto.ov.cgdefi() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get global statistics about Decentralized Finances [Source: CoinGecko]
    </p>

* **Returns**

    pandas.DataFrame
        Metric, Value

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.cgdefi(
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Shows global statistics about Decentralized Finances. [Source: CoinGecko]
    </p>

* **Parameters**

    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

