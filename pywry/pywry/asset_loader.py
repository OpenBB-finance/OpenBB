"""Asset loader for CSS and JavaScript files.

Provides caching and hash-based asset IDs for hot reload functionality.
"""

from __future__ import annotations

import hashlib

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from .log import warn


if TYPE_CHECKING:
    from .config import AssetSettings


class AssetLoader:
    """Loads and caches CSS and JavaScript files.

    Provides hash-based asset IDs for efficient hot reload detection.
    """

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialize the asset loader.

        Parameters
        ----------
        base_dir : Path or None, optional
            Base directory for resolving relative paths.
            Defaults to current working directory.
        """
        self._base_dir = base_dir or Path.cwd()
        self._cache: dict[Path, str] = {}
        self._hash_cache: dict[Path, str] = {}

    @property
    def base_dir(self) -> Path:
        """Get the base directory for resolving paths."""
        return self._base_dir

    @base_dir.setter
    def base_dir(self, value: Path) -> None:
        """Set the base directory."""
        self._base_dir = value

    def resolve_path(self, path: str | Path) -> Path:
        """Resolve a path relative to the base directory.

        Parameters
        ----------
        path : str or Path
            Absolute or relative path.

        Returns
        -------
        Path
            Resolved absolute path.
        """
        p = Path(path)
        if p.is_absolute():
            return p
        return (self._base_dir / p).resolve()

    def load_css(self, path: str | Path, use_cache: bool = True) -> str:
        """Load a CSS file.

        Parameters
        ----------
        path : str or Path
            Path to the CSS file.
        use_cache : bool, optional
            Whether to use cached content.

        Returns
        -------
        str
            CSS file content, or empty string on error.
        """
        resolved = self.resolve_path(path)

        if use_cache and resolved in self._cache:
            return self._cache[resolved]

        try:
            content = resolved.read_text(encoding="utf-8")
            self._cache[resolved] = content
            self._update_hash(resolved, content)
            return content
        except Exception as e:
            warn(f"Failed to load CSS file {resolved}: {e}")
            return ""

    def load_script(self, path: str | Path, use_cache: bool = True) -> str:
        """Load a JavaScript file.

        Parameters
        ----------
        path : str or Path
            Path to the JavaScript file.
        use_cache : bool, optional
            Whether to use cached content.

        Returns
        -------
        str
            JavaScript file content, or empty string on error.
        """
        resolved = self.resolve_path(path)

        if use_cache and resolved in self._cache:
            return self._cache[resolved]

        try:
            content = resolved.read_text(encoding="utf-8")
            self._cache[resolved] = content
            self._update_hash(resolved, content)
            return content
        except Exception as e:
            warn(f"Failed to load script file {resolved}: {e}")
            return ""

    def load_all_css(self, paths: list[str | Path]) -> str:
        """Load and concatenate multiple CSS files.

        Parameters
        ----------
        paths : list of str or Path
            List of paths to CSS files.

        Returns
        -------
        str
            Concatenated CSS content.
        """
        parts = []
        for path in paths:
            content = self.load_css(path)
            if content:
                parts.append(f"/* Source: {path} */\n{content}")
        return "\n\n".join(parts)

    def load_all_scripts(self, paths: list[str | Path]) -> list[str]:
        """Load multiple JavaScript files.

        Parameters
        ----------
        paths : list of str or Path
            List of paths to JavaScript files.

        Returns
        -------
        list of str
            List of script contents in order.
        """
        return [self.load_script(path) for path in paths]

    def get_asset_id(self, path: str | Path) -> str:
        """Get a unique asset ID based on path and content hash.

        The ID is stable across reloads if content hasn't changed.

        Parameters
        ----------
        path : str or Path
            Path to the asset file.

        Returns
        -------
        str
            Asset ID string suitable for use as HTML element ID.
        """
        resolved = self.resolve_path(path)

        # Get or compute hash
        if resolved not in self._hash_cache:
            # Load file to populate hash cache
            self.load_css(resolved)

        content_hash = self._hash_cache.get(resolved, "unknown")
        # Use just the filename and first 8 chars of hash for readable IDs
        name = resolved.stem.replace(".", "-").replace(" ", "-")
        return f"pywry-css-{name}-{content_hash[:8]}"

    def _update_hash(self, path: Path, content: str) -> None:
        """Update the content hash for a file."""
        self._hash_cache[path] = hashlib.sha256(content.encode()).hexdigest()

    def has_changed(self, path: str | Path) -> bool:
        """Check if a file has changed since last load.

        Parameters
        ----------
        path : str or Path
            Path to check.

        Returns
        -------
        bool
            True if file content has changed, False otherwise.
        """
        resolved = self.resolve_path(path)
        old_hash = self._hash_cache.get(resolved)

        if old_hash is None:
            return True

        try:
            content = resolved.read_text(encoding="utf-8")
            new_hash = hashlib.sha256(content.encode()).hexdigest()
            return old_hash != new_hash
        except Exception:
            return True

    def invalidate(self, path: str | Path) -> None:
        """Invalidate cached content for a file.

        Parameters
        ----------
        path : str or Path
            Path to invalidate.
        """
        resolved = self.resolve_path(path)
        self._cache.pop(resolved, None)
        # Keep hash for change detection

    def clear_cache(self) -> None:
        """Clear all cached content."""
        self._cache.clear()
        self._hash_cache.clear()


_asset_loader: AssetLoader | None = None


def get_asset_loader() -> AssetLoader:
    """Get the global asset loader instance."""
    global _asset_loader
    if _asset_loader is None:
        _asset_loader = AssetLoader()
    return _asset_loader


def configure_asset_loader(
    base_dir: Path | None = None,
    settings: AssetSettings | None = None,
) -> AssetLoader:
    """Configure and return the global asset loader.

    Parameters
    ----------
    base_dir : Path or None, optional
        Base directory for resolving paths.
    settings : AssetSettings or None, optional
        Asset settings to apply.

    Returns
    -------
    AssetLoader
        Configured asset loader instance.
    """
    global _asset_loader

    if base_dir is None and settings is not None and settings.path:
        base_dir = Path(settings.path)

    _asset_loader = AssetLoader(base_dir=base_dir)
    return _asset_loader


@lru_cache(maxsize=32)
def build_style_tag(css: str, asset_id: str) -> str:
    """Build a style tag with the given CSS content.

    Parameters
    ----------
    css : str
        CSS content.
    asset_id : str
        ID for the style element.

    Returns
    -------
    str
        HTML style tag string.
    """
    return f'<style id="{asset_id}">\n{css}\n</style>'


@lru_cache(maxsize=32)
def build_script_tag(script: str, asset_id: str | None = None) -> str:
    """Build a script tag with the given JavaScript content.

    Parameters
    ----------
    script : str
        JavaScript content.
    asset_id : str or None, optional
        Optional ID for the script element.

    Returns
    -------
    str
        HTML script tag string.
    """
    if asset_id:
        return f'<script id="{asset_id}">\n{script}\n</script>'
    return f"<script>\n{script}\n</script>"
