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
alt.oss.summary(
    repo: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get repository summary
    </p>

* **Parameters**

    repo : str
            Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame - Columns: Metric, Value

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
alt.oss.summary(
    repo: str,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display repo summary [Source: https://api.github.com]
    </p>

* **Parameters**

    repo : str
            Repository to display summary. Format: org/repo, e.g., openbb-finance/openbbterminal
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

