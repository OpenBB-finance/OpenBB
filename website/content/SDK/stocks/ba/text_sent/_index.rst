.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Find the sentiment of a post and related comments
    </h3>

{{< highlight python >}}
stocks.ba.text_sent(
    post_data: List[str]
) -> float
{{< /highlight >}}

* **Parameters**

    post_data: list[str]
        A post and its comments in string form

    
* **Returns**

    float
        A number in the range [-1, 1] representing sentiment
    