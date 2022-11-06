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
forecast.desc(
    df: pandas.core.frame.DataFrame,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Returns statistics for a given df
    </p>

* **Parameters**

    df: *pd.DataFrame*
        The df to produce statistics for
    chart: *bool*
       Flag to display chart


* **Returns**

    df: *pd.DataFrame*
        The df with the new data

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

