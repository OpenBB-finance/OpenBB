.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Helper methods for querying graphql api. [Source: https://bitquery.io/]
    </h3>

{{< highlight python >}}
crypto.onchain.query_graph(
    url: str,
    query: str,
) -> dict
{{< /highlight >}}

* **Parameters**

    url: *str*
        Endpoint url
    query: *str*
        Graphql query

    
* **Returns**

    dict:
        Dictionary with response data
    