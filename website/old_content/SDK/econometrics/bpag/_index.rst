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
econometrics.bpag(
    model: pandas.core.frame.DataFrame,
    chart: bool = False,
) -> tuple
{{< /highlight >}}

.. raw:: html

    <p>
    Calculate test statistics for heteroscedasticity
    </p>

* **Parameters**

    model : OLS Model
        Model containing residual values.
    chart: bool
       Flag to display chart


* **Returns**

    Test results from the Breusch-Pagan Test

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
econometrics.bpag(
    model: pandas.core.frame.DataFrame,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Show Breusch-Pagan heteroscedasticity test
    </p>

* **Parameters**

    model : OLS Model
        Model containing residual values.
    export : str
        Format to export data
    chart: bool
       Flag to display chart

