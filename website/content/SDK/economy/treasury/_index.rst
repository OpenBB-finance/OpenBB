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
economy.treasury(
    instruments: list = None,
    maturities: list = None,
    frequency: str = 'monthly',
    start_date: str = '1900-01-01',
    end_date: str = None,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get U.S. Treasury rates [Source: EconDB]
    </p>

* **Parameters**

    instruments: list
        Type(s) of treasuries, nominal, inflation-adjusted (long term average) or secondary market.
        Available options can be accessed through economy.treasury_maturities().
    maturities : list
        Treasury maturities to get. Available options can be accessed through economy.treasury_maturities().
    frequency : str
        Frequency of the data, this can be annually, monthly, weekly or daily.
    start_date : str
        Starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : str
        End date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    chart: bool
       Flag to display chart


* **Returns**

    treasury_data: pd.Dataframe
        Holds data of the selected types and maturities

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
economy.treasury(
    instruments: list = None,
    maturities: list = None,
    frequency: str = 'monthly',
    start_date: str = '1900-01-01',
    end_date: str = None,
    raw: bool = False,
    external_axes: Optional[List[axes]] = None,
    export: str = '',
    chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Display U.S. Treasury rates [Source: EconDB]
    </p>

* **Parameters**

    instruments: list
        Type(s) of treasuries, nominal, inflation-adjusted or secondary market.
        Available options can be accessed through economy.treasury_maturities().
    maturities : list
        Treasury maturities to display. Available options can be accessed through economy.treasury_maturities().
    frequency : str
        Frequency of the data, this can be daily, weekly, monthly or annually
    start_date : str
        Starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : str
        End date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    raw : bool
        Whether to display the raw output.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    chart: bool
       Flag to display chart


* **Returns**

    Plots the Treasury Series.
