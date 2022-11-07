.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.onchain.query_graph(
    url: str,
    query: str,
    chart: bool = False,
) -> dict
{{< /highlight >}}

.. raw:: html

    <p>
    Helper methods for querying graphql api. [Source: https://bitquery.io/]
    </p>

* **Parameters**

    url: str
        Endpoint url
    query: str
        Graphql query

* **Returns**

    dict:
        Dictionary with response data
