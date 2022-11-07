.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.fa.similar_dfs(
    symbol: str,
    info: Dict[str, Any],
    n: int,
    no_filter: bool = False,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get dataframes for similar companies
    </p>

* **Parameters**

    symbol : str
        The ticker symbol to create a dataframe for
    into : Dict[str,Any]
        The dictionary produced from the yfinance.info function
    n : int
        The number of similar companies to produce
    no_filter : bool
        True means that we do not filter based on market cap

* **Returns**

    new_list : List[str, pd.DataFrame]
        A list of similar companies
