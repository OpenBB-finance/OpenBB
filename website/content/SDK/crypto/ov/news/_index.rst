.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.ov.news(
    limit: int = 60,
    post_kind: str = 'news',
    filter_: Optional[str] = None,
    region: str = 'en',
    source: Optional[str] = None,
    symbol: Optional[str] = None,
    sortby: str = 'published_at',
    ascend: bool = True,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    limit: *int*
        number of news to fetch
    post_kind: *str*
        Filter by category of news. Available values: *news or media.*
    filter_: Optional[str]
        Filter by kind of news. One from list: rising|hot|bullish|bearish|important|saved|lol
    region: *str*
        Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch),
        es (Español), fr (Français), it (Italiano), pt (Português), ru (Русский)
    sortby: *str*
        Key to sort by.
    ascend: *bool*
        Sort in ascend order.

    
* **Returns**

    pd.DataFrame
        DataFrame with recent news from different sources filtered by provided parameters.
   