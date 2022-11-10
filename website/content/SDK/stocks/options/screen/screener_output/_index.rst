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
stocks.options.screen.screener_output(
    preset: str,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

.. raw:: html

    <p>
    Screen options based on preset filters
    </p>

* **Parameters**

    preset: str
        Chosen preset
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame:
        DataFrame with screener data, or empty if errors
    str:
        String containing error message if supplied

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.options.screen.screener_output(
    preset: str,
    limit: int = 20,
    export: str = '',
    chart: bool = False,
) -> List
{{< /highlight >}}

.. raw:: html

    <p>
    Print the output of screener
    </p>

* **Parameters**

    preset: str
        Chosen preset
    limit: int
        Number of randomly sorted rows to display
    export: str
        Format for export file
    chart: bool
       Flag to display chart


* **Returns**

    List
        List of tickers screened
