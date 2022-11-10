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
stocks.options.chains(
    symbol: str,
    expiry: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Display option chains [Source: Tradier]"
    </p>

* **Parameters**

    symbol : str
        Ticker to get options for
    expiry : str
        Expiration date in the form of "YYYY-MM-DD"
    chart: bool
       Flag to display chart


* **Returns**

    chains: pd.DataFrame
        Dataframe with options for the given Symbol and Expiration date

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.options.chains(
    symbol: str,
    expiry: str,
    to_display: List[str] = None,
    min_sp: float = -1,
    max_sp: float = -1,
    calls_only: bool = False,
    puts_only: bool = False,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display option chain
    </p>

* **Parameters**

    symbol: str
        Stock ticker symbol
    expiry: str
        Expiration date of option
    to_display: List[str]
        List of columns to display
    min_sp: float
        Min strike price to display
    max_sp: float
        Max strike price to display
    calls_only: bool
        Only display calls
    puts_only: bool
        Only display puts
    export: str
        Format to  export file
    chart: bool
       Flag to display chart

