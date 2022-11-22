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
stocks.th.all() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get all exchanges.

    Parameters
    ----------
    </p>

* **Parameters**

    
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        All available exchanges

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.th.all()
{{< /highlight >}}

.. raw:: html

    <p>
    Display all exchanges.

    Parameters
    ----------
    </p>

* **Parameters**

    
    chart: bool
       Flag to display chart

