.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
stocks.ba.text_sent(
    post_data: List[str],
    chart: bool = False,
) -> float
{{< /highlight >}}

.. raw:: html

    <p>
    Find the sentiment of a post and related comments
    </p>

* **Parameters**

    post_data: list[str]
        A post and its comments in string form

* **Returns**

    float
        A number in the range [-1, 1] representing sentiment
