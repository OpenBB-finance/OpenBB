.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Load a Excel file with views for Black Litterman model.
    </h3>

{{< highlight python >}}
portfolio.po.load_bl_views(
    excel\_file: str = '',
    )
{{< /highlight >}}

* **Parameters**

    excel\_file: *str*
        The location of the Excel file that needs to be loaded.

    
* **Returns**

    p\_views: *list*
        Returns a list with p\_views matrix
    q\_views: *list*
        Returns a list with q\_views matrix
    