import json
import sys
import os
import subprocess

settings = json.load(sys.stdin)

print("settings", settings)

for key, value in settings.items():
    if not isinstance(value, dict) and not isinstance(value, list):
        os.environ[key] = value

from terminal import terminal

terminal()
