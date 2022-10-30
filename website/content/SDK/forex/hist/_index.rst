.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get historical forex data.
    </h3>

{{< highlight python >}}
forex.hist(
    to\_symbol: str = 'USD',
    from\_symbol: str = 'EUR',
    resolution: str = 'd',
    interval: int = 5,
    start\_date: str = '',
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    to\_symbol : *str*
        To forex symbol
    from\_symbol : *str*
        From forex symbol
    resolution : str, optional
        Resolution of data.  Can be "i", "d", "w", "m" for intraday, daily, weekly or monthly
    interval : int, optional
        Interval for intraday data
    start\_date : str, optional
        Start date for data.

    
* **Returns**

    pd.DataFrame
        Historical data for forex pair
    