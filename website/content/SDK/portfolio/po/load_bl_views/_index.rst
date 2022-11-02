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
    excel_file: str = '',
)
{{< /highlight >}}

* **Parameters**

    excel_file: *str*
        The location of the Excel file that needs to be loaded.

    
* **Returns**

    p_views: *list*
        Returns a list with p_views matrix
    q_views: *list*
        Returns a list with q_views matrix
   