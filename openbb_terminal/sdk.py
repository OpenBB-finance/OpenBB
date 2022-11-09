from openbb_terminal.core.library.breadcrumb import Breadcrumb
from openbb_terminal.core.library.trail_map import TrailMap
from openbb_terminal.core.library.breadcrumb import MetadataBuilder

trail = ""
trail_map = TrailMap()
metadata = MetadataBuilder.build(trail=trail, trail_map=trail_map)


openbb = Breadcrumb(
    metadata=metadata,
    trail=trail,
    trail_map=trail_map,
)