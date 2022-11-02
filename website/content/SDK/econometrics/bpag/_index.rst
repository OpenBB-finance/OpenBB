.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate test statistics for heteroscedasticity
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter.
Use the :python:`external_axes` argument to provide axes of external figures.

{{< highlight python >}}
econometrics.bpag(
    model: pandas.core.frame.DataFrame,
    chart: bool = False,
    external_axes: Optional[List[plt.Axes]] = None,
) -> tuple
{{< /highlight >}}

* **Parameters**

    model : *OLS Model*
        Model containing residual values.
    chart: *bool*
       Flag to display chart
    external_axes: Optional[List[plt.Axes]]
        List of external axes to include in plot

* **Returns**

    Test results from the Breusch-Pagan Test
