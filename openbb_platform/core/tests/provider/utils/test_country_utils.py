"""Tests for country_utils module."""

import pytest
from openbb_core.provider.utils.country_utils import CountryParam
from pydantic import BaseModel, ValidationError


class CountryTestModel(BaseModel):
    """Test model for CountryParam validation."""

    country: CountryParam | None = None


class TestCountryParam:
    """Tests for CountryParam type."""

    def test_iso_alpha2_code(self):
        """ISO alpha-2 codes should be accepted and normalized."""
        model = CountryTestModel(country="US")
        assert model.model_dump()["country"] == "us"

        model = CountryTestModel(country="us")
        assert model.model_dump()["country"] == "us"

        model = CountryTestModel(country="DE")
        assert model.model_dump()["country"] == "de"

    def test_country_name(self):
        """Full country names should resolve to alpha-2 codes."""
        model = CountryTestModel(country="United States")
        assert model.model_dump()["country"] == "us"

        model = CountryTestModel(country="Germany")
        assert model.model_dump()["country"] == "de"

        model = CountryTestModel(country="United Kingdom")
        assert model.model_dump()["country"] == "gb"

    def test_lower_snake_case(self):
        """lower_snake_case names should be accepted."""
        model = CountryTestModel(country="united_states")
        assert model.model_dump()["country"] == "us"

        model = CountryTestModel(country="united_kingdom")
        assert model.model_dump()["country"] == "gb"

    def test_none_value(self):
        """None values should pass through."""
        model = CountryTestModel(country=None)
        assert model.country is None

    def test_invalid_country(self):
        """Invalid country names should raise ValidationError."""
        with pytest.raises(ValidationError):
            CountryTestModel(country="InvalidCountry")

        with pytest.raises(ValidationError):
            CountryTestModel(country="XX")  # Invalid ISO code
