.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ba.spacc(
    limit: int = 10,
    popular: bool = False,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, dict]
{{< /highlight >}}

.. raw:: html

    <p>
    Get top tickers from r/SPACs [Source: reddit]
    </p>

* **Parameters**

    limit : int
        Number of posts to look at
    popular : bool
        Search by hot instead of new

* **Returns**

    pd.DataFrame:
        Dataframe of reddit submission
    dict:
        Dictionary of tickers and number of mentions
