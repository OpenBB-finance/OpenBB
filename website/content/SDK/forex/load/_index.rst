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
    start_date: str = '2021-11-02',
    source: str = 'YahooFinance',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Loads forex for two given symbols
    </p>

* **Parameters**

    to_symbol : *str*
        The from currency symbol. Ex: USD, EUR, GBP, YEN
    from_symbol: *str*
        The from currency symbol. Ex: USD, EUR, GBP, YEN
    resolution: *str*
        The resolution for the data
    interval: *str*
        What interval to get data for
    start_date: *str*
        When to begin loading in data
    source: *str*
        Where to get data from

* **Returns**

    pd.DataFrame
        The loaded data
