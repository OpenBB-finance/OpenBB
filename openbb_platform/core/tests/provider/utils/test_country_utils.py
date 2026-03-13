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

    def test_groups_property(self):
        """Country should expose membership groups."""
        c = Country("US")
        groups = c.groups
        assert isinstance(groups, list)
        assert "G7" in groups
        assert "G20" in groups
        assert "NATO" in groups
        assert "OECD" in groups
        # US is not a member of these
        assert "EU" not in groups
        assert "OPEC" not in groups

    def test_groups_empty_for_non_member(self):
        """Countries not in any tracked group should have empty groups list."""
        # Most small countries won't be in any group
        c = Country("Fiji")
        assert c.groups == []

    def test_is_member_of(self):
        """is_member_of should check group membership."""
        c = Country("Germany")
        assert c.is_member_of("G7") is True
        assert c.is_member_of("EU") is True
        assert c.is_member_of("NATO") is True
        assert c.is_member_of("OECD") is True
        assert c.is_member_of("OPEC") is False
        assert c.is_member_of("BRICS") is False

    def test_is_member_of_case_insensitive(self):
        """is_member_of should be case-insensitive."""
        c = Country("FR")
        assert c.is_member_of("g7") is True
        assert c.is_member_of("G7") is True
        assert c.is_member_of("Eu") is True

    def test_opec_members(self):
        """OPEC members should be correctly identified."""
        opec_countries = ["SA", "AE", "KW", "IQ", "IR", "VE", "NG"]
        for code in opec_countries:
            c = Country(code)
            assert c.is_member_of("OPEC") is True, f"{code} should be OPEC member"

    def test_brics_members(self):
        """BRICS members should be correctly identified."""
        brics_countries = ["BR", "RU", "IN", "CN", "ZA"]
        for code in brics_countries:
            c = Country(code)
            assert c.is_member_of("BRICS") is True, f"{code} should be BRICS member"

    def test_eu_members(self):
        """EU members should be correctly identified."""
        eu_countries = ["DE", "FR", "IT", "ES", "NL", "BE", "PL"]
        for code in eu_countries:
            c = Country(code)
            assert c.is_member_of("EU") is True, f"{code} should be EU member"
        c = Country("GB")
        assert c.is_member_of("EU") is False

    @pytest.mark.parametrize(
        "input_name, expected_alpha2",
        [
            ("Curacao", "CW"),
            ("Reunion", "RE"),
            ("Aland Islands", "AX"),
            ("Saint Barthelemy", "BL"),
            ("Turkiye", "TR"),
            ("Turkey", "TR"),
            ("Cote d'Ivoire", "CI"),
        ],
    )
    def test_ascii_normalized_names(self, input_name, expected_alpha2):
        """ASCII variants of accented country names should resolve correctly."""
        c = Country(input_name)
        assert c.alpha_2 == expected_alpha2

    @pytest.mark.parametrize(
        "input_name, expected_alpha2",
        [
            ("Curaçao", "CW"),
            ("Réunion", "RE"),
            ("Åland Islands", "AX"),
            ("Saint Barthélemy", "BL"),
            ("Türkiye", "TR"),
            ("Côte d'Ivoire", "CI"),
        ],
    )
    def test_accented_names(self, input_name, expected_alpha2):
        """Accented country names should resolve correctly."""
        c = Country(input_name)
        assert c.alpha_2 == expected_alpha2
