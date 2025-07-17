"""OpenBB Core."""

import sys
import warnings

if sys.version_info < (3, 10):
    warnings.warn(
        "Support for Python versions below 3.10 will be deprecated in a future release of OpenBB Core.",
        FutureWarning,
        stacklevel=2,
    )
