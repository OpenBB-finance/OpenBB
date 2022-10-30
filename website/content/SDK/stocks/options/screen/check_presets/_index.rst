.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Checks option screener preset values
    </h3>

{{< highlight python >}}
stocks.options.screen.check_presets(
    preset\_dict: dict,
    ) -> str
{{< /highlight >}}

* **Parameters**

    preset\_dict: *dict*
        Defined presets from configparser
    
* **Returns**

    error: *str*
        String of all errors accumulated
    