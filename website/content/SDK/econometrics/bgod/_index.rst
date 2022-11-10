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
econometrics.bgod(
    model: pandas.core.frame.DataFrame,
    lags: int = 3,
    chart: bool = False,
) -> tuple
{{< /highlight >}}

.. raw:: html

    <p>
    Calculate test statistics for autocorrelation
    </p>

* **Parameters**

    model : OLS Model
        Model containing residual values.
    lags : int
        The amount of lags.
    chart: bool
       Flag to display chart


* **Returns**

    Test results from the Breusch-Godfrey Test

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
econometrics.bgod(
    model: pandas.core.frame.DataFrame,
    lags: int = 3,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Show Breusch-Godfrey autocorrelation test
    </p>

* **Parameters**

    model : OLS Model
        Model containing residual values.
    lags : int
        The amount of lags included.
    export : str
        Format to export data
    chart: bool
       Flag to display chart

