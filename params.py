from pathlib import Path

from openbb_terminal.core.plots.backend import plots_backend

plots_backend().start(True)
args = plots_backend().call_routine(
    "test", ["this", "cucumbers", "that"], Path(__file__).parent / "test.html"
)

for key, value in args.items():
    print(key, value)
