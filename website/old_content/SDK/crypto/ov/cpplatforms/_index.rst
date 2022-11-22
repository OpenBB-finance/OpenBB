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
crypto.ov.cpplatforms() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama ... [Source: CoinPaprika]
    </p>

* **Returns**

    pandas.DataFrame
        index, platform_id

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.cpplatforms(
    export: str,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama.
    [Source: CoinPaprika]
    </p>

* **Parameters**

    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

