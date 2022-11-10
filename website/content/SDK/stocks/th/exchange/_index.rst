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
stocks.th.exchange(
    symbol: str,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get current exchange open hours.
    </p>

* **Parameters**

    symbol : str
        Exchange symbol
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Exchange info

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
stocks.th.exchange(
    symbol: str,
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display current exchange trading hours.
    </p>

* **Parameters**

    symbol : str
        Exchange symbol
    chart: bool
       Flag to display chart

