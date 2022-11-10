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
crypto.disc.trending() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns trending coins [Source: CoinGecko]

    Parameters
    ----------
    </p>

* **Parameters**

    
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame:
        Trending Coins

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.disc.trending(
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display trending coins [Source: CoinGecko]
    </p>

* **Parameters**

    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

