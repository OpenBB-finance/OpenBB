.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get repository stats
    </h3>

{{< highlight python >}}
alt.oss.github_data(
    url: str,
    **kwargs,
    )
{{< /highlight >}}

* **Parameters**

    url: *str*
        github api endpoint
    params: *dict*
        params to pass to api endpoint
    
* **Returns**

    dict with data
    