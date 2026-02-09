"""Tests for country_utils module."""

import pytest
from openbb_core.provider.utils.country_utils import Country, CountryParam
from pydantic import BaseModel, ValidationError


class CountryTestModel(BaseModel):
    """Test model for Country validation."""

    country: Country | None = None


class TestCountry:
    """Tests for Country type."""

    def test_iso_alpha2_code(self):
        """ISO alpha-2 codes should be accepted."""
        model = CountryTestModel(country="US")
        assert str(model.country) == "US"
        assert model.country.alpha_2 == "US"
        assert model.country.alpha_3 == "USA"

        model = CountryTestModel(country="us")
        assert str(model.country) == "US"

        model = CountryTestModel(country="DE")
        assert str(model.country) == "DE"
        assert model.country.alpha_3 == "DEU"

    def test_iso_alpha3_code(self):
        """ISO alpha-3 codes should be accepted."""
        model = CountryTestModel(country="USA")
        assert str(model.country) == "US"
        assert model.country.alpha_2 == "US"
        assert model.country.alpha_3 == "USA"

        model = CountryTestModel(country="deu")
        assert str(model.country) == "DE"

    def test_country_name(self):
        """Full country names should resolve to alpha-2 codes."""
        model = CountryTestModel(country="United States")
        assert str(model.country) == "US"
        assert model.country.name == "United States"

        model = CountryTestModel(country="Germany")
        assert str(model.country) == "DE"
        assert model.country.name == "Germany"

        model = CountryTestModel(country="United Kingdom")
        assert str(model.country) == "GB"

    def test_lower_snake_case(self):
        """lower_snake_case names should be accepted."""
        model = CountryTestModel(country="united_states")
        assert str(model.country) == "US"

        model = CountryTestModel(country="united_kingdom")
        assert str(model.country) == "GB"

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

    def test_country_properties(self):
        """Country should expose all ISO properties."""
        c = Country("US")
        assert c.alpha_2 == "US"
        assert c.alpha_3 == "USA"
        assert c.name == "United States"
        assert c.numeric == "840"

    def test_str_inheritance(self):
        """Country should behave like a string."""
        c = Country("US")
        assert isinstance(c, str)
        assert c == "US"
        assert c.lower() == "us"
        assert f"Country: {c}" == "Country: US"

    def test_model_dump(self):
        """model_dump should serialize to string."""
        model = CountryTestModel(country="united_states")
        dumped = model.model_dump()
        assert dumped["country"] == "US"

    def test_country_param_alias(self):
        """CountryParam should be an alias for Country."""
        assert CountryParam is Country
