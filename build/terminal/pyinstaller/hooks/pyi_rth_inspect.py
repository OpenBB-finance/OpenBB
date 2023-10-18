# Runtime hook copied from  pyinstaller


import inspect
import os
import sys

# pylint:disable=W0622,W0212,E1101

_orig_inspect_getsourcefile = inspect.getsourcefile


# Provide custom implementation of inspect.getsourcefile() for frozen applications that properly resolves relative
# filenames obtained from object (e.g., inspect stack-frames). See #5963.
def _pyi_getsourcefile(object):
    filename = inspect.getfile(object)
    if not os.path.isabs(filename):
        # Check if given filename matches the basename of __main__'s __file__.
        if hasattr(sys.modules["__main__"], "__file__"):
            main_file = sys.modules["__main__"].__file__
            if filename == os.path.basename(main_file):
                return main_file

        # If filename ends with .py suffix and does not correspond to frozen entry-point script, convert it to
        # corresponding .pyc in sys._MEIPASS.
        if filename.endswith(".py"):
            filename = os.path.normpath(os.path.join(sys._MEIPASS, filename + "c"))
            # Ensure the relative path did not try to jump out of sys._MEIPASS, just in case...
            if filename.startswith(sys._MEIPASS):
                return filename
    elif filename.startswith(sys._MEIPASS) and filename.endswith(".pyc"):
        # If filename is already PyInstaller-compatible, prevent any further processing (i.e., with original
        # implementation).
        return filename
    # Use original implementation as a fallback.
    return _orig_inspect_getsourcefile(object)


inspect.getsourcefile = _pyi_getsourcefile
