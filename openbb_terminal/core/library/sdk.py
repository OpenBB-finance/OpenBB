from openbb_terminal.core.library.breadcrumb import Breadcrumb
from openbb_terminal.core.library.trail_map import TrailMap
from openbb_terminal.core.library.operation import OperationBuilder


trail_map = TrailMap()
operation_builder = OperationBuilder(trail_map=trail_map)

openbb = Breadcrumb(
    trail="",
    trail_map=trail_map,
    operation_builder=operation_builder,
)
