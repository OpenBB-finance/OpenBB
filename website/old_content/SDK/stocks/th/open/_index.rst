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
stocks.th.open() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get open exchanges.

    Parameters
    ----------
    </p>

* **Parameters**

    
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Currently open exchanges

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.th.open()
{{< /highlight >}}

.. raw:: html

    <p>
    Display open exchanges.

    Parameters
    ----------
    </p>

* **Parameters**

    
    chart: bool
       Flag to display chart

