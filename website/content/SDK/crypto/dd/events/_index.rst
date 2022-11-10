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
crypto.dd.events(
    symbol: str = 'eth-ethereum', sortby='date',
    ascend: bool = False,
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get all events related to given coin like conferences, start date of futures trading etc.
    [Source: CoinPaprika]

    Example of response from API:

    .. code-block:: json

    {
        "id": "17398-cme-april-first-trade",
        "date": "2018-04-02T00:00:00Z",
        "date_to": "string",
        "name": "CME: April First Trade",
        "description": "First trade of Bitcoin futures contract for April 2018.",
        "is_conference": false,
        "link": "http://www.cmegroup.com/trading/equity-index/us-index/bitcoin_product_calendar_futures.html",
        "proof_image_link": "https://static.coinpaprika.com/storage/cdn/event_images/16635.jpg"
    }
    </p>

* **Parameters**

    symbol: str
        id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum'
    sortby: str
        Key by which to sort data. Every column name is valid
        (see for possible values:
        https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1events/get).
    ascend: bool
        Flag to sort data ascending
    chart: bool
       Flag to display chart


* **Returns**

    pandas.DataFrame
        Events found for given coin
        Columns: id, date , date_to, name, description, is_conference, link, proof_image_link

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.dd.events(
    symbol: str = 'BTC',
    limit: int = 10,
    sortby: str = 'date',
    ascend: bool = False,
    links: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Get all events for given coin id. [Source: CoinPaprika]
    </p>

* **Parameters**

    symbol: str
        Cryptocurrency symbol (e.g. BTC)
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data. Every column name is valid
        (see for possible values:
        https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1events/get).
    ascend: bool
        Flag to sort data ascending
    links: bool
        Flag to display urls
    export : str
        Export dataframe data to csv,json,xlsx file
    chart: bool
       Flag to display chart

