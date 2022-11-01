.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate test statistics for Durbing Watson autocorrelation
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
econometrics.dwat(
    residual: pandas.core.frame.DataFrame,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    residual : *OLS Model*
        Model containing residual values.

    
* **Returns**

    Test statistic of the Durbin Watson test.
    