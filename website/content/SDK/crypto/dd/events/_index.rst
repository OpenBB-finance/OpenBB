.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get all events related to given coin like conferences, start date of futures trading etc.
    [Source: CoinPaprika]

    Example of response from API:

    .. code-block:: *json*

    {
        "id": "17398-cme-april-first-trade",
        "date": "2018-04-02T00:00:00Z",
        "date\_to": "string",
        "name": "CME: April First Trade",
        "description": "First trade of Bitcoin futures contract for April 2018.",
        "is\_conference": false,
        "link": "http://www.cmegroup.com/trading/equity-index/us-index/bitcoin\_product\_calendar\_futures.html",
        "proof\_image\_link": "https://static.coinpaprika.com/storage/cdn/event\_images/16635.jpg"
    }
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.dd.events(
    symbol: str = 'eth-ethereum', sortby='date', ascend: bool = False,
    chart: bool = False,
    ) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    symbol: *str*
        id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum'
    sortby: *str*
        Key by which to sort data. Every column name is valid
        (see for possible values:
        https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin\_id%7D~1events/get).
    ascend: *bool*
        Flag to sort data ascending
    
* **Returns**

    pandas.DataFrame
        Events found for given coin
        Columns: id, date , date\_to, name, description, is\_conference, link, proof\_image\_link
    