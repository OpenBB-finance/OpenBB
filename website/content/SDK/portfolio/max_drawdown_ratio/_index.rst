.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Calculate the drawdown (MDD) of historical series.  Note that the calculation is done
     on cumulative returns (or prices).  The definition of drawdown is

     DD = (current value - rolling maximum) / rolling maximum
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
portfolio.max_drawdown_ratio(
    portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel,
    is_returns: bool = False,
    chart: bool = False,
    ) -> pandas.core.series.Series
{{< /highlight >}}

* **Parameters**

    data: *pd.Series*
        Series of input values
    is_returns: *bool*
        Flag to indicate inputs are returns

    
* **Returns**

    pd.Series
        Holdings series
    pd.Series
        Drawdown series
    