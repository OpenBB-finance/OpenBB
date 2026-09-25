{%- set views_class = cookiecutter.router_name.replace('_', ' ').title().replace(' ', '') -%}
"""Charting views for the {{ cookiecutter.router_name }} router."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure


class {{ views_class }}Views:
    """Charts for {{ cookiecutter.router_name }} commands, one static method per route."""

    @staticmethod
    def {{ cookiecutter.router_name }}_candles(
        **kwargs: Any,
    ) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Chart the daily high prices returned by ``/{{ cookiecutter.router_name }}/candles``.

        Parameters
        ----------
        **kwargs : Any
            The charting context, with the command's rows in ``obbject_item``.

        Returns
        -------
        tuple[OpenBBFigure, dict[str, Any]]
            The figure and its JSON-serializable content.
        """
        from openbb_charting.core.openbb_figure import OpenBBFigure

        rows = kwargs["obbject_item"]
        fig = OpenBBFigure()
        fig.add_bar(x=[row.date for row in rows], y=[row.high for row in rows])
        content = fig.show(external=True).to_plotly_json()
        return fig, content
