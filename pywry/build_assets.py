"""Convenience script for downloading CDN asset files."""

from __future__ import annotations

import gzip

from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


# Asset URLs - use full bundle which includes templates (plotly_dark, plotly_white, etc.)
PLOTLY_JS_URL = "https://cdn.plot.ly/plotly-3.3.1.js"
AGGRID_JS_URL = (
    "https://cdn.jsdelivr.net/npm/ag-grid-community@35.0.0/dist/ag-grid-community.min.js"
)
AGGRID_CSS_BASE_URL = "https://cdn.jsdelivr.net/npm/ag-grid-community@35.0.0/styles"

# OpenBB icon URL (placeholder - should be replaced with actual URL)
OPENBB_ICON_URL = (
    "https://raw.githubusercontent.com/OpenBB-finance/OpenBB/main/images/openbb_logo.png"
)

# Asset directory
ASSETS_DIR = Path(__file__).parent / "pywry" / "frontend" / "assets"


def ensure_assets_dir() -> None:
    """Ensure the assets directory exists."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def download_file(url: str, dest: Path, description: str) -> bool:
    """Download a file from a URL and compress it with gzip.

    Parameters
    ----------
    url : str
        The URL to download from.
    dest : Path
        The destination path (will be saved as .gz compressed).
    description : str
        Description for logging.

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    print(f"Downloading {description}...")

    try:
        with urlopen(url, timeout=60) as response:  # noqa: S310
            content = response.read()
    except URLError as e:
        print(f"  ✗ Failed to download {description}: {e}")
        return False
    except OSError as e:
        print(f"  ✗ Failed to write {description}: {e}")
        return False

    # Compress with gzip and save with .gz extension
    gz_dest = Path(str(dest) + ".gz")
    gz_dest.write_bytes(gzip.compress(content, compresslevel=9))
    original_size_kb = len(content) / 1024
    compressed_size_kb = gz_dest.stat().st_size / 1024
    ratio = (1 - compressed_size_kb / original_size_kb) * 100
    print(
        f"  ✓ Downloaded {description} "
        f"({original_size_kb:.0f} KB → {compressed_size_kb:.0f} KB, {ratio:.0f}% smaller)"
    )
    return True


def download_plotly_js() -> bool:
    """Download Plotly.js library (full bundle with templates)."""
    dest = ASSETS_DIR / "plotly-3.3.1.js"
    gz_dest = Path(str(dest) + ".gz")
    if gz_dest.exists():
        print(f"Plotly.js already exists at {gz_dest}")
        return True
    return download_file(PLOTLY_JS_URL, dest, "Plotly.js v3.3.1 (full bundle)")


def download_aggrid_js() -> bool:
    """Download AG Grid JS library."""
    dest = ASSETS_DIR / "ag-grid-community-35.0.0.min.js"
    gz_dest = Path(str(dest) + ".gz")
    if gz_dest.exists():
        print(f"AG Grid JS already exists at {gz_dest}")
        return True
    return download_file(AGGRID_JS_URL, dest, "AG Grid v35.0.0")


def download_aggrid_css() -> bool:
    """Download AG Grid CSS files."""
    themes = ["quartz", "alpine", "balham", "material"]
    modes = ["light", "dark"]

    success = True

    # Download base styles
    base_dest = ASSETS_DIR / "ag-grid-35.0.0.css"
    base_gz_dest = Path(str(base_dest) + ".gz")
    if not base_gz_dest.exists():
        base_url = f"{AGGRID_CSS_BASE_URL}/ag-grid.css"
        if not download_file(base_url, base_dest, "AG Grid base CSS"):
            success = False

    # Download theme-specific CSS
    for theme in themes:
        for mode in modes:
            filename = f"ag-theme-{theme}-{mode}-35.0.0.css"
            dest = ASSETS_DIR / filename
            gz_dest = Path(str(dest) + ".gz")

            if gz_dest.exists():
                print(f"AG Grid {theme} {mode} CSS already exists")
                continue

            # AG Grid themes are packaged differently
            css_url = f"{AGGRID_CSS_BASE_URL}/ag-theme-{theme}.css"
            if not download_file(css_url, dest, f"AG Grid {theme} theme"):
                success = False

    return success


def create_placeholder_files() -> None:
    """Create placeholder files if downloads fail."""
    placeholder_files = [
        ("plotly-3.3.1.min.js.gz", b"// Plotly.js placeholder - download failed\n"),
        (
            "ag-grid-community-35.0.0.min.js.gz",
            b"// AG Grid placeholder - download failed\n",
        ),
        ("ag-grid-35.0.0.css.gz", b"/* AG Grid CSS placeholder - download failed */\n"),
    ]

    for filename, content in placeholder_files:
        dest = ASSETS_DIR / filename
        if not dest.exists():
            print(f"Creating placeholder for {filename}")
            dest.write_bytes(gzip.compress(content, compresslevel=9))


def download_all_assets() -> bool:
    """Download all required assets.

    Returns
    -------
    bool
        True if all assets were downloaded successfully.
    """
    ensure_assets_dir()

    results = [
        download_plotly_js(),
        download_aggrid_js(),
        download_aggrid_css(),
    ]

    success = all(results)

    if not success:
        print("\nSome downloads failed. Creating placeholders...")
        create_placeholder_files()

    return success


def verify_assets() -> dict[str, bool]:
    """Verify that all required assets exist.

    Returns
    -------
    dict[str, bool]
        Dictionary mapping asset names to their existence status.
    """
    required_assets = [
        "plotly-3.3.1.js.gz",  # Full bundle with templates
        "ag-grid-community-35.0.0.min.js.gz",
        "ag-grid-35.0.0.css.gz",
    ]

    return {asset: (ASSETS_DIR / asset).exists() for asset in required_assets}


def main() -> None:
    """Main entry point for the build script."""
    print("PyWry Asset Download Script")
    print("=" * 40)

    download_all_assets()

    print("\nAsset verification:")
    status = verify_assets()
    for asset, exists in status.items():
        marker = "✓" if exists else "✗"
        print(f"  {marker} {asset}")

    if all(status.values()):
        print("\nAll assets are ready!")
    else:
        print("\nWarning: Some assets are missing. PyWry may not function correctly.")


if __name__ == "__main__":
    main()
