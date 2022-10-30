.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get company managers from Business Insider
    </h3>

{{< highlight python >}}
stocks.fa.mgmt(
    symbol: str,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Stock ticker symbol

    
* **Returns**

    pd.DataFrame
        Dataframe of managers
    