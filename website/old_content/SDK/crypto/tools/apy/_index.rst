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
crypto.tools.apy(
    apr: float,
    compounding_times: int,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

.. raw:: html

    <p>
    Converts apr into apy
    </p>

* **Parameters**

    apr: float
        value in percentage
    compounding_times: int
        number of compounded periods in a year
    chart: bool
       Flag to display chart


* **Returns**

    Tuple:
        - pd.DataFrame: dataframe with results
        - str: narrative version of results

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.tools.apy(
    apr: float,
    compounding_times: int,
    narrative: bool = False,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Displays APY value converted from APR
    </p>

* **Parameters**

    apr: float
        value in percentage
    compounding_times: int
        number of compounded periods in a year
    narrative: str
        display narrative version instead of dataframe
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart


* **Returns**

    
