"""Views for the {{ cookiecutter.router_name }} Extension."""

# flake8: noqa: PLR0912
# pylint: disable=import-outside-toplevel,too-few-public-methods

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure  # `openbb-charting` is Optional for the user.


# You can make charts that are returned when you map a function
# route in lower_snake_case to this class using static methods.
# You can return whatever format you like, but it must be JSON-serializable.
# The returned tuple object gets added to the response object from the application.
# The charting extension itself is accessible under the `charting` namespace.
# While the finished chart is under the `chart` object of the OBBject response output.
# The application will check if the user has `openbb-charting` installed on run.
# If not, the views are not added to the application.


class {{cookiecutter.router_name.replace("_", " ").title().replace(" ", "")}}Views:
    """{{ cookiecutter.router_name }} Views."""

    @staticmethod
    def {{cookiecutter.router_name}}_candles(**kwargs) -> tuple["OpenBBFigure", dict[str, Any]]:
        """Create a chart that will return to the API as a JSON-encoded string."""
        # Keep imports here so they are imported only at function run.
        from openbb_charting.core.openbb_figure import OpenBBFigure

        data = kwargs["obbject_item"]  # This is where the data will always be.

        print(data)

        fig = OpenBBFigure()

        fig.add_bar(x=[d.date for d in data], y=[d.high for d in data])
        content = fig.show(external=True).to_plotly_json()
        # fig should be the binary Python object of the chart
        # content should be a JSON-serialized version ready for the frontend to render.
        return fig, content
