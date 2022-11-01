.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate test statistics for autocorrelation
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
econometrics.bgod(
    model: pandas.core.frame.DataFrame,
    lags: int = 3,
    chart: bool = False
) -> tuple
{{< /highlight >}}

* **Parameters**

    model : *OLS Model*
        Model containing residual values.
    lags : *int*
        The amount of lags.

    
* **Returns**

    Test results from the Breusch-Godfrey Test
    