.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
alt.oss.github_data(
    url: str,
    **kwargs, chart: bool = False,
)
{{< /highlight >}}

.. raw:: html

    <p>
    Get repository stats
    </p>

* **Parameters**

    url: str
        github api endpoint
    params: dict
        params to pass to api endpoint

* **Returns**

    dict with data
