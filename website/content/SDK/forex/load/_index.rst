.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
forex.load(
    to_symbol: str,
    from_symbol: str,
    resolution: str = 'd',
    interval: str = '1day',
    start_date: str = None,
    source: str = 'YahooFinance',
    verbose: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Load forex for two given symbols.
    </p>

* **Parameters**

    to_symbol : str
        The from currency symbol. Ex: USD, EUR, GBP, YEN
    from_symbol : str
        The from currency symbol. Ex: USD, EUR, GBP, YEN
    resolution : str, optional
        The resolution for the data, by default "d"
    interval : str, optional
        What interval to get data for, by default "1day"
    start_date : str, optional
        When to begin loading in data, by default last_year.strftime("%Y-%m-%d")
    source : str, optional
        Where to get data from, by default "YahooFinance"
    verbose : bool, optional
        Display verbose information on what was the pair that was loaded, by default True

* **Returns**

    pd.DataFrame
        The loaded data
