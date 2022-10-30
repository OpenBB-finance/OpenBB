.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get repository summary
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
alt.oss.summary(
    repo: str,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    repo : *str*
            Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal

    
* **Returns**

    pd.DataFrame - Columns: Metric, Value
    