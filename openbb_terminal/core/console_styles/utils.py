import json
import os
from pathlib import Path
from typing import Dict


def get_console_style(name: str, folder: Path) -> Dict[str, str]:
    """Get console style based on rich style."""
    file_name = name + ".richstyle.json"
    file = folder / file_name

    if os.path.exists(file):
        with open(file) as f:
            return json.load(f)
    return {}
