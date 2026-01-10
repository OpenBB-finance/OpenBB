#!/usr/bin/env python3
"""Build script to create the Plotly widget bundle.

This script combines Plotly.js with the widget render function into a single
JavaScript bundle file that can be used as the _esm for anywidget.

Similar to how plotly.py builds their widgetbundle.js.
"""

from __future__ import annotations

import gzip

from pathlib import Path


ASSETS_DIR = Path(__file__).parent / "pywry" / "frontend" / "assets"
SRC_DIR = Path(__file__).parent / "pywry" / "frontend" / "src"
OUTPUT_FILE = ASSETS_DIR / "plotly-widgetbundle.js"


def build_bundle() -> None:
    """Build the Plotly widget bundle."""
    # Read compressed Plotly.js
    plotly_gz = ASSETS_DIR / "plotly-3.3.1.js.gz"
    if not plotly_gz.exists():
        raise FileNotFoundError(f"Plotly.js not found: {plotly_gz}")

    with gzip.open(plotly_gz, "rt", encoding="utf-8") as f:
        plotly_js = f.read()

    # Read the widget render function from src
    widget_js = SRC_DIR / "plotly-widget.js"
    if not widget_js.exists():
        raise FileNotFoundError(f"Widget JS not found: {widget_js}")

    with widget_js.open(encoding="utf-8") as f:
        widget_code = f.read()

    # Combine: first define Plotly globally, then the widget module
    bundle = f"""\
// PyWry Plotly Widget Bundle - Built with build_widget.py
// This file includes Plotly.js and the widget render function.

// === Plotly.js ===
{plotly_js}

// === Widget Module ===
{widget_code}
"""

    # Write the bundle
    OUTPUT_FILE.write_text(bundle, encoding="utf-8")
    print(f"Built: {OUTPUT_FILE}")
    print(f"Size: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} MB")

    # Also create a gzipped version
    gz_file = OUTPUT_FILE.with_suffix(".js.gz")
    with gzip.open(gz_file, "wt", encoding="utf-8") as f:
        f.write(bundle)
    print(f"Built: {gz_file}")
    print(f"Size: {gz_file.stat().st_size / 1024 / 1024:.2f} MB (gzipped)")


if __name__ == "__main__":
    build_bundle()
