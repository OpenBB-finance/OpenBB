.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets messages from given user [Source: stocktwits]
    </h3>

{{< highlight python >}}
stocks.ba.stalker(
    user: str,
    limit: int = 30
) -> List[Dict]
{{< /highlight >}}

* **Parameters**

    user : *str*
        User to get posts for
    limit : int, optional
        Number of posts to get, by default 30
    