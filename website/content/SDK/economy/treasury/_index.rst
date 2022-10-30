.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get U.S. Treasury rates [Source: EconDB]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
economy.treasury(
    instruments: list = None,
    maturities: list = None,
    frequency: str = 'monthly',
    start\_date: str = '1900-01-01', end\_date: str = '2022-10-30', chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    instruments: *list*
        Type(s) of treasuries, nominal, inflation-adjusted (long term average) or secondary market.
        Available options can be accessed through economy.treasury\_maturities().
    maturities : *list*
        Treasury maturities to get. Available options can be accessed through economy.treasury\_maturities().
    frequency : *str*
        Frequency of the data, this can be annually, monthly, weekly or daily.
    start\_date : *str*
        Starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end\_date : *str*
        End date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.

    
* **Returns**

    treasury\_data: *pd.Dataframe*
        Holds data of the selected types and maturities
    