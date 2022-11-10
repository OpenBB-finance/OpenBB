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
crypto.tools.il(
    price_changeA: float,
    price_changeB: float,
    proportion: float,
    initial_pool_value: float,
    chart: bool = False,
) -> Tuple[pandas.core.frame.DataFrame, str]
{{< /highlight >}}

.. raw:: html

    <p>
    Calculates Impermanent Loss in a custom liquidity pool
    </p>

* **Parameters**

    price_changeA: float
        price change of crypto A in percentage
    price_changeB: float
        price change of crypto B in percentage
    proportion: float
        percentage of first token in pool
    initial_pool_value: float
        initial value that pool contains
    chart: bool
       Flag to display chart


* **Returns**

    Tuple:
        - pd.DataFrame: dataframe with results
        - str: narrative version of results

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.tools.il(
    price_changeA: int,
    price_changeB: int,
    proportion: int,
    initial_pool_value: int,
    narrative: bool = False,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Displays Impermanent Loss in a custom liquidity pool
    </p>

* **Parameters**

    price_changeA: float
        price change of crypto A in percentage
    price_changeB: float
        price change of crypto B in percentage
    proportion: float
        percentage of first token in pool
    initial_pool_value: float
        initial value that pool contains
    narrative: str
        display narrative version instead of dataframe
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart


* **Returns**

    
