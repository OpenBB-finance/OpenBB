from pathlib import Path

HOME_DIRECTORY = Path.home()
OPENBB_DIRECTORY = Path(HOME_DIRECTORY, ".openbb_sdk")
# This is being used for plotly to find the plugins, not good using relative references,
# will likely break under site_packages
REPOSITORY_DIRECTORY = Path(__file__).parent.parent.parent.parent.parent
