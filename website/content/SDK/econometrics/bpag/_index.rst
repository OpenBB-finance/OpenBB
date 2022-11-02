.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate test statistics for heteroscedasticity
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
econometrics.bpag(
    model: pandas.core.frame.DataFrame,
    chart: bool = False,
) -> tuple
{{< /highlight >}}

* **Parameters**

    model : *OLS Model*
        Model containing residual values.

    
* **Returns**

    Test results from the Breusch-Pagan Test
   