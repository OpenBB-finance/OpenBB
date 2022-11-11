.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ba.stalker(
    user: str,
    limit: int = 30,
    chart: bool = False,
) -> List[Dict]
{{< /highlight >}}

.. raw:: html

    <p>
    Gets messages from given user [Source: stocktwits]
    </p>

* **Parameters**

    user : str
        User to get posts for
    limit : int, optional
        Number of posts to get, by default 30
