from openbb_core.app.model.obbject import OBBject, OBBjectPluginInterface
import warnings

# pluginmodule1.py
class OBBjectPlugin(OBBjectPluginInterface):
    def extend_obbject(self, obbject):
        def put_your_method_here(self):
            return "This is a new method added by OBBjectPlugin."

        # This can be better too.
        if hasattr(obbject, "your_method"):
            warnings.warn(
                "OBBject already has a method called 'your_method'.  Overwriting."
            )

        setattr(obbject, "your_method", put_your_method_here)
