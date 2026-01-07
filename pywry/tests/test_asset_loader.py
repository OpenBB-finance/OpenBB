"""Tests for asset_loader module.

Tests AssetLoader class for loading CSS and JavaScript files.
"""

from pathlib import Path

from pywry.asset_loader import AssetLoader


class TestAssetLoaderInit:
    """Tests for AssetLoader initialization."""

    def test_creates_default_loader(self):
        """Creates loader with default settings."""
        loader = AssetLoader()
        assert loader is not None

    def test_accepts_base_dir(self):
        """Accepts custom base directory."""
        loader = AssetLoader(base_dir=Path(__file__).parent)
        assert loader.base_dir == Path(__file__).parent

    def test_default_base_dir_is_cwd(self):
        """Default base directory is current working directory."""
        loader = AssetLoader()
        assert loader.base_dir == Path.cwd()

    def test_initializes_cache(self):
        """Initializes empty cache."""
        loader = AssetLoader()
        assert hasattr(loader, "_cache")
        assert isinstance(loader._cache, dict)


class TestBaseDirProperty:
    """Tests for base_dir property."""

    def test_gets_base_dir(self):
        """Gets base directory."""
        test_dir = Path(__file__).parent
        loader = AssetLoader(base_dir=test_dir)
        assert loader.base_dir == test_dir

    def test_sets_base_dir(self):
        """Sets base directory."""
        loader = AssetLoader()
        new_dir = Path(__file__).parent
        loader.base_dir = new_dir
        assert loader.base_dir == new_dir


class TestResolvePath:
    """Tests for resolve_path method."""

    def test_resolves_relative_path(self):
        """Resolves relative path to absolute."""
        loader = AssetLoader()
        result = loader.resolve_path("test.css")
        assert result.is_absolute()

    def test_resolves_absolute_path(self):
        """Returns absolute path unchanged."""
        loader = AssetLoader()
        absolute = Path(__file__).resolve()
        result = loader.resolve_path(str(absolute))
        assert result == absolute

    def test_resolves_path_object(self):
        """Handles Path object input."""
        loader = AssetLoader()
        path = Path("test.css")
        result = loader.resolve_path(path)
        assert isinstance(result, Path)

    def test_resolves_against_base_dir(self):
        """Resolves relative paths against base_dir."""
        base = Path(__file__).parent
        loader = AssetLoader(base_dir=base)
        result = loader.resolve_path("test.css")
        assert result.parent == base.resolve()


class TestLoadCss:
    """Tests for load_css method."""

    def test_loads_existing_css_file(self, tmp_path):
        """Loads content from existing CSS file."""
        css_file = tmp_path / "test.css"
        css_file.write_text("body { color: red; }")
        loader = AssetLoader(base_dir=tmp_path)
        result = loader.load_css("test.css")
        assert "body { color: red; }" in result

    def test_returns_empty_for_missing_file(self, tmp_path):
        """Returns empty string for missing file."""
        loader = AssetLoader(base_dir=tmp_path)
        result = loader.load_css("missing.css")
        assert result == ""

    def test_caches_css_content(self, tmp_path):
        """Caches loaded CSS content."""
        css_file = tmp_path / "cached.css"
        css_file.write_text("body { margin: 0; }")
        loader = AssetLoader(base_dir=tmp_path)
        loader.load_css("cached.css")
        # Modify file
        css_file.write_text("body { margin: 10px; }")
        # Should return cached version (use_cache=True by default)
        result = loader.load_css("cached.css")
        assert "margin: 0" in result

    def test_bypasses_cache_when_disabled(self, tmp_path):
        """Bypasses cache when use_cache=False."""
        css_file = tmp_path / "nocache.css"
        css_file.write_text("body { margin: 0; }")
        loader = AssetLoader(base_dir=tmp_path)
        loader.load_css("nocache.css")
        # Modify file
        css_file.write_text("body { margin: 10px; }")
        # Should return fresh content
        result = loader.load_css("nocache.css", use_cache=False)
        assert "margin: 10px" in result


class TestLoadScript:
    """Tests for load_script method."""

    def test_loads_existing_js_file(self, tmp_path):
        """Loads content from existing JS file."""
        js_file = tmp_path / "test.js"
        js_file.write_text("console.log('hello');")
        loader = AssetLoader(base_dir=tmp_path)
        result = loader.load_script("test.js")
        assert "console.log('hello');" in result

    def test_returns_empty_for_missing_file(self, tmp_path):
        """Returns empty string for missing file."""
        loader = AssetLoader(base_dir=tmp_path)
        result = loader.load_script("missing.js")
        assert result == ""

    def test_caches_script_content(self, tmp_path):
        """Caches loaded script content."""
        js_file = tmp_path / "cached.js"
        js_file.write_text("let x = 1;")
        loader = AssetLoader(base_dir=tmp_path)
        loader.load_script("cached.js")
        resolved = loader.resolve_path("cached.js")
        assert resolved in loader._cache

    def test_bypasses_cache_when_disabled(self, tmp_path):
        """Bypasses cache when use_cache=False."""
        js_file = tmp_path / "nocache.js"
        js_file.write_text("let x = 1;")
        loader = AssetLoader(base_dir=tmp_path)
        loader.load_script("nocache.js")
        # Modify file
        js_file.write_text("let x = 2;")
        # Should return fresh content
        result = loader.load_script("nocache.js", use_cache=False)
        assert "let x = 2" in result


class TestLoadAllCss:
    """Tests for load_all_css method."""

    def test_loads_multiple_css_files(self, tmp_path):
        """Loads and concatenates multiple CSS files."""
        css1 = tmp_path / "file1.css"
        css2 = tmp_path / "file2.css"
        css1.write_text("body { color: red; }")
        css2.write_text("h1 { font-size: 2em; }")
        loader = AssetLoader(base_dir=tmp_path)
        result = loader.load_all_css(["file1.css", "file2.css"])
        assert "color: red" in result
        assert "font-size: 2em" in result

    def test_handles_empty_list(self):
        """Handles empty list of paths."""
        loader = AssetLoader()
        result = loader.load_all_css([])
        assert result == ""


class TestLoadAllScripts:
    """Tests for load_all_scripts method."""

    def test_loads_multiple_js_files(self, tmp_path):
        """Loads multiple JavaScript files."""
        js1 = tmp_path / "script1.js"
        js2 = tmp_path / "script2.js"
        js1.write_text("console.log('one');")
        js2.write_text("console.log('two');")
        loader = AssetLoader(base_dir=tmp_path)
        result = loader.load_all_scripts(["script1.js", "script2.js"])
        assert len(result) == 2
        assert "console.log('one');" in result[0]
        assert "console.log('two');" in result[1]

    def test_handles_empty_list(self):
        """Handles empty list of paths."""
        loader = AssetLoader()
        result = loader.load_all_scripts([])
        assert result == []


class TestClearCache:
    """Tests for clear_cache method."""

    def test_clears_all_cached_content(self, tmp_path):
        """Clears all cached content."""
        css_file = tmp_path / "test.css"
        css_file.write_text("body {}")
        loader = AssetLoader(base_dir=tmp_path)
        loader.load_css("test.css")
        assert len(loader._cache) > 0
        loader.clear_cache()
        assert len(loader._cache) == 0

    def test_invalidate_clears_specific_path(self, tmp_path):
        """Invalidate clears cache for specific path."""
        css1 = tmp_path / "file1.css"
        css2 = tmp_path / "file2.css"
        css1.write_text("body {}")
        css2.write_text("h1 {}")
        loader = AssetLoader(base_dir=tmp_path)
        loader.load_css("file1.css")
        loader.load_css("file2.css")
        # Use invalidate method to clear specific path
        loader.invalidate("file1.css")
        # file2 should still be cached
        resolved2 = loader.resolve_path("file2.css")
        assert resolved2 in loader._cache


class TestFileWatching:
    """Tests for file watching support."""

    def test_has_hash_cache(self):
        """Has hash cache for change detection."""
        loader = AssetLoader()
        assert hasattr(loader, "_hash_cache")

    def test_tracks_file_hashes(self, tmp_path):
        """Tracks file content hashes."""
        css_file = tmp_path / "tracked.css"
        css_file.write_text("body { color: blue; }")
        loader = AssetLoader(base_dir=tmp_path)
        loader.load_css("tracked.css")
        resolved = loader.resolve_path("tracked.css")
        assert resolved in loader._hash_cache
