.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > This functions groups the data queried from the EconDB database [Source: EconDB]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
economy.macro(
    parameters: list = None,
    countries: list = None,
    transform: str = '',
    start_date: str = '1900-01-01', end_date=datetime.date(
    2022, 11, 1, chart: bool = False,
), symbol: str = '',
    chart: bool = False,
) -> Tuple[Any, Dict[Any, Dict[Any, Any]], str]
{{< /highlight >}}

* **Parameters**

    parameters: *list*
        The type of data you wish to download. Available parameters can be accessed through economy.macro_parameters().
    countries : *list*
        The selected country or countries. Available countries can be accessed through economy.macro_countries().
    transform : *str*
        The selected transform. Available transforms can be accessed through get_macro_transform().
    start_date : *str*
        The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : *str*
        The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    symbol : *str*
        In what currency you wish to convert all values.

    
* **Returns**

    pd.DataFrame
        A DataFrame with the requested macro data of all chosen countries
    Dictionary
        A dictionary containing the units of each country's parameter (e.g. EUR)
    str
        Denomination which can be Trillions, Billions, Millions, Thousands
    