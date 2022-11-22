.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
alt.oss._make_request(
    url: str,
    chart: bool = False,
) -> Optional[bs4.BeautifulSoup]
{{< /highlight >}}

.. raw:: html

    <p>
    Helper method to scrap
    </p>

* **Parameters**

    url : str
        url to scrape

* **Returns**

    BeautifulSoup object
