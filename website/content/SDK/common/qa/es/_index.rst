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
common.qa.es(
    data: pandas.core.frame.DataFrame,
    use_mean: bool = False,
    distribution: str = 'normal',
    percentile: Union[float, int] = 99.9,
    portfolio: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Gets Expected Shortfall for specified stock dataframe.
    </p>

* **Parameters**

    data: pd.DataFrame
        Data dataframe
    use_mean: bool
        If one should use the data mean for calculation
    distribution: str
        Type of distribution, options: laplace, student_t, normal
    percentile: Union[float,int]
        VaR percentile
    portfolio: bool
        If the data is a portfolio
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame with Expected Shortfall per percentile

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
common.qa.es(
    data: pandas.core.frame.DataFrame,
    symbol: str = '',
    use_mean: bool = False,
    distribution: str = 'normal',
    percentile: float = 99.9,
    portfolio: bool = False,
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Displays expected shortfall.
    </p>

* **Parameters**

    data: pd.DataFrame
        Data dataframe
    use_mean:
        if one should use the data mean return
    symbol: str
        name of the data
    distribution: str
        choose distribution to use: logistic, laplace, normal
    percentile: int
        es percentile
    portfolio: bool
        If the data is a portfolio
    chart: bool
       Flag to display chart

