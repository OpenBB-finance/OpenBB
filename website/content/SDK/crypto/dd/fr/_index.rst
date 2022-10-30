.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns coin fundraising
    [Source: https://messari.io/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.fr(
    symbol: str,
    chart: bool = False,
    ) -> Tuple[str, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame, pandas.core.frame.DataFrame]
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto symbol to check fundraising

    
* **Returns**

    str
        launch summary
    pd.DataFrame
        Sales rounds
    pd.DataFrame
        Treasury Accounts
    pd.DataFrame
        Metric Value launch details
    