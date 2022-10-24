from openbb_terminal.core.config.paths import PACKAGE_ENV_FILE
from openbb_terminal.loggers import get_commit_hash

commit_hash = get_commit_hash(use_env=False)

with PACKAGE_ENV_FILE.open("w") as f:
    f.write(f"OPENBB_LOGGING_COMMIT_HASH='{commit_hash}'")
    f.write("\n")
    f.write("OPENBB_LOGGING_APP_NAME='gst_packaged_pypi'")
