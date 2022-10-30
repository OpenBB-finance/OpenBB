.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get repository star history
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
alt.oss.history(repo: str, chart = False)
{{< /highlight >}}

* **Parameters**

    repo : *str*
            Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal

    
* **Returns**

    pd.DataFrame - Columns: Date, Stars
    