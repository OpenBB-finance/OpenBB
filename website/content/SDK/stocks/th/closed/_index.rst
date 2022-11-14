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
stocks.th.closed() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get closed exchanges.

    Parameters
    ----------
    </p>

* **Parameters**

    
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Currently closed exchanges

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.th.closed()
{{< /highlight >}}

.. raw:: html

    <p>
    Display closed exchanges.

    Parameters
    ----------
    </p>

* **Parameters**

    
    chart: bool
       Flag to display chart

