import pkg_resources
from openbb_provider.provider.provider_registry import Builder, ProviderRegistry


# This could get more complicated as we add more things.
def build_registry() -> ProviderRegistry:
    builder = Builder()
    extensions = []

    entry_points = pkg_resources.iter_entry_points("openbb_provider_extension")
    for entry_point in entry_points:
        extensions.append(entry_point.load())

    builder.add_providers(extensions)
    return builder.build()
