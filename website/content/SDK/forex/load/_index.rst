.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Loads forex for two given symbols
    </h3>

{{< highlight python >}}
forex.load(
    to\_symbol: str,
    from\_symbol: str,
    resolution: str = 'd',
    interval: str = '1day',
    start\_date: str = '2021-10-31', source: str = 'YahooFinance',
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

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
    