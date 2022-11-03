from openbb_terminal.core.library.breadcrumb import Breadcrumb
from openbb_terminal.core.library.trail_map import TrailMap
from openbb_terminal.core.library.operation import OperationBuilder
from openbb_terminal.core.library.breadcrumb import MetadataBuilder


trail = ""
trail_map = TrailMap()
metadata = MetadataBuilder.build(trail=trail, trail_map=trail_map)
operation_builder = OperationBuilder(trail_map=trail_map)

openbb = Breadcrumb(
    metadata=metadata,
    operation_builder=operation_builder,
    trail=trail,
    trail_map=trail_map,
)
