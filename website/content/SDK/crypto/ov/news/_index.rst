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

.. raw:: html

    <p>
    Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]
    </p>

* **Parameters**

    limit: int
        number of news to fetch
    post_kind: str
        Filter by category of news. Available values: news or media.
    filter\_: Optional[str]
        Filter by kind of news. One from list: rising|hot|bullish|bearish|important|saved|lol
    region: str
        Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch),
        es (Español), fr (Français), it (Italiano), pt (Português), ru (Русский)
    sortby: str
        Key to sort by.
    ascend: bool
        Sort in ascend order.
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        DataFrame with recent news from different sources filtered by provided parameters.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.ov.news(
    post_kind: str = 'news',
    region: str = 'en',
    filter_: Optional[str] = None,
    limit: int = 25,
    sortby: str = 'published_at',
    ascend: bool = False,
    links: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display recent posts from CryptoPanic news aggregator platform.
    [Source: https://cryptopanic.com/]
    </p>

* **Parameters**

    limit: int
        number of news to display
    post_kind: str
        Filter by category of news. Available values: news or media.
    filter\_: Optional[str]
        Filter by kind of news. One from list: rising|hot|bullish|bearish|important|saved|lol
    region: str
        Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch),
        es (Español), fr (Français), it (Italiano), pt (Português), ru (Русский)
    sortby: str
        Key to sort by.
    ascend: bool
        Sort in ascending order.
    links: bool
        Show urls for news
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

