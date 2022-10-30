.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Returns  a list of developer activity for a given coin and time interval.

    [Source: https://santiment.net/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.gh(
    symbol: str,
    dev\_activity: bool = False,
    interval: str = '1d',
    start\_date: str = '2021-10-30T23:20:37Z',
    end\_date: str = '2022-10-30T23:20:37Z',
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol : *str*
        Crypto symbol to check github activity
    dev\_activity: *bool*
        Whether to filter only for development activity
    start\_date : *int*
        Initial date like string (e.g., 2021-10-01)
    end\_date : *int*
        End date like string (e.g., 2021-10-01)
    interval : *str*
        Interval frequency (e.g., 1d)

    
* **Returns**

    pd.DataFrame
        developer activity over time
    