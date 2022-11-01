.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get currently set API keys.
    </h3>

{{< highlight python >}}
keys.mykeys(
    show: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    show: *bool*
        Flag to choose whether to show actual keys or not.
        By default, False.

    
* **Returns**

    pd.DataFrame
        Currents keys
    