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
crypto.onchain.gwei() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns the most recent Ethereum gas fees in gwei
    [Source: https://ethgasstation.info]

    Parameters
    ----------
    </p>

* **Parameters**

    
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        four gas fees and durations
            (fees for slow, average, fast and
            fastest transactions in gwei and
            its average durations in seconds)

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.onchain.gwei(
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Current gwei fees
    [Source: https://ethgasstation.info]
    </p>

* **Parameters**

    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

