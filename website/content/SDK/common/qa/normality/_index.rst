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
common.qa.normality(
    data: pandas.core.frame.DataFrame,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Look at the distribution of returns and generate statistics on the relation to the normal curve.
    This function calculates skew and kurtosis (the third and fourth moments) and performs both
    a Jarque-Bera and Shapiro Wilk test to determine if data is normally distributed.
    </p>

* **Parameters**

    data : pd.DataFrame
        Dataframe of targeted data
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Dataframe containing statistics of normality

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.qa.normality(
    data: pandas.core.frame.DataFrame,
    target: str,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    View normality statistics
    </p>

* **Parameters**

    data : pd.DataFrame
        DataFrame
    target : str
        Column in data to look at
    export : str
        Format to export data
    chart: bool
       Flag to display chart

