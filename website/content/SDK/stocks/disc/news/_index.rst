.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets news. [Source: SeekingAlpha]
    </h3>

{{< highlight python >}}
stocks.disc.news(
    news\_type: str = 'Top-News', limit: int = 5,
    ) -> List
{{< /highlight >}}

* **Parameters**

    news_type : *str*
        From: Top-News, On-The-Move, Market-Pulse, Notable-Calls, Buybacks, Commodities, Crypto, Issuance, Global,
        Guidance, IPOs, SPACs, Politics, M-A, Consumer, Energy, Financials, Healthcare, MLPs, REITs, Technology
    limit : *int*
        Number of news to display

    
* **Returns**

    List[dict]
        List of dict news
    