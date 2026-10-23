"""Tests for the update_country_data module."""

import importlib.util
import sys
from unittest.mock import MagicMock, patch

import pytest

HAS_PYCOUNTRY = importlib.util.find_spec("pycountry") is not None

if HAS_PYCOUNTRY:
    from openbb_core.provider.utils.update_country_data import (
        NAME_INDEX,
        _build_name_index,
        _strip_accents,
        build_country_data,
        resolve_country,
    )
else:
    mock_pycountry = MagicMock()
    mock_bs4 = MagicMock()
    sys.modules["pycountry"] = mock_pycountry
    sys.modules["bs4"] = mock_bs4

    from openbb_core.provider.utils.update_country_data import (
        NAME_INDEX,
        _build_name_index,
        _strip_accents,
        build_country_data,
        resolve_country,
    )


@pytest.mark.skipif(not HAS_PYCOUNTRY, reason="pycountry not installed")
class TestCountryDataUtils:
    """Test country data utility functions."""

    def test_strip_accents(self):
        """Test accent stripping."""
        assert _strip_accents("Côte d'Ivoire") == "Cote d'Ivoire"
        assert _strip_accents("España") == "Espana"
        assert _strip_accents("Türkiye") == "Turkiye"

    def test_build_name_index(self):
        """Test name index building."""
        index = _build_name_index()
        assert isinstance(index, dict)
        assert len(index) > 0
        assert "united states" in index
        assert index["united states"] == "US"
        assert index.get("brunei") == "BN"

    def test_resolve_country_by_exact_name(self):
        """Test resolving countries by exact name."""
        assert resolve_country("United States") == "US"
        assert resolve_country("France") == "FR"
        assert resolve_country("Germany") == "DE"

    def test_resolve_country_by_common_name(self):
        """Test resolving countries by common names."""
        assert resolve_country("USA") == "US"
        assert resolve_country("UK") == "GB"
        assert resolve_country("Holland") == "NL"

    def test_resolve_country_with_wiki_references(self):
        """Test resolving countries with Wikipedia reference markers."""
        assert resolve_country("United States[1]") == "US"
        assert resolve_country("France[2]") == "FR"

    def test_resolve_country_with_parentheticals(self):
        """Test resolving countries with parenthetical notes."""
        assert resolve_country("United Kingdom (UK)") == "GB"
        assert resolve_country("South Korea (ROK)") == "KR"

    def test_resolve_country_with_extra_whitespace(self):
        """Test resolving countries with extra whitespace."""
        assert resolve_country("  United States  ") == "US"
        assert resolve_country("\tFrance\n") == "FR"

    def test_resolve_country_not_found(self):
        """Test resolving non-existent countries when fuzzy search finds nothing."""
        with patch(
            "openbb_core.provider.utils.update_country_data.pycountry.countries.search_fuzzy",
            side_effect=LookupError,
        ):
            assert resolve_country("XYZ Country") is None

    def test_resolve_country_non_country_entity(self):
        """Test resolving non-country entities."""
        assert resolve_country("European Union") is None
        assert resolve_country("African Union") is None

    def test_name_index_has_core_entries(self):
        """Test that NAME_INDEX contains expected core entries."""
        assert NAME_INDEX["united states"] == "US"
        assert NAME_INDEX["france"] == "FR"
        assert NAME_INDEX["united kingdom"] == "GB"

    @patch("openbb_core.provider.utils.update_country_data.fetch_soup")
    def test_build_country_data_with_mocked_scrapers(self, mock_fetch_soup):
        """Test building country data with mocked web scrapers."""
        mock_soup = MagicMock()
        mock_soup.find_all.return_value = []
        mock_soup.find.return_value = None
        mock_fetch_soup.return_value = mock_soup

        mock_country = MagicMock(alpha_2="US", alpha_3="USA", numeric="840")
        mock_country.name = "United States"

        with patch(
            "openbb_core.provider.utils.update_country_data.pycountry.countries",
            [mock_country],
        ):
            data = build_country_data()

            assert isinstance(data, dict)
            assert "_last_updated" in data
            assert "_sources" in data
            assert "countries" in data
            assert isinstance(data["countries"], list)

    def test_resolve_country_case_insensitive(self):
        """Test that country resolution is case-insensitive."""
        assert resolve_country("FRANCE") == "FR"
        assert resolve_country("france") == "FR"
        assert resolve_country("FrAnCe") == "FR"

    def test_resolve_country_special_cases(self):
        """Test special case country name mappings."""
        assert resolve_country("Czechia") == "CZ"
        assert resolve_country("Czech Republic") == "CZ"
        assert resolve_country("Türkiye") == "TR"
        assert resolve_country("Turkey") == "TR"
