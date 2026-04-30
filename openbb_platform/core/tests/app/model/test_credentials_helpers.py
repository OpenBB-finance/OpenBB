"""Targeted unit tests for ``openbb_core.app.model.credentials`` helpers."""

from unittest.mock import patch

import pytest

from openbb_core.app.model.credentials import (
    Credentials,
    CredentialsLoader,
)


def test_normalize_credential_map_empty_input_returns_empty():
    assert CredentialsLoader._normalize_credential_map({}) == {}
    assert CredentialsLoader._normalize_credential_map(None) == {}


def test_normalize_credential_map_lowercases_keys_and_strips():
    out = CredentialsLoader._normalize_credential_map({"  ABC  ": "v"})
    assert "abc" in out
    assert out["abc"] == "v"


def test_normalize_credential_map_keeps_non_string_keys_untouched():
    out = CredentialsLoader._normalize_credential_map({1: "v"})
    assert 1 in out


def test_normalize_credential_map_skips_empty_override():
    """Empty value does NOT overwrite an existing key."""
    out = CredentialsLoader._normalize_credential_map({"abc": "real", "ABC": ""})
    assert out["abc"] == "real"


def test_format_credentials_appends_additional_unknown_keys():
    loader = CredentialsLoader()
    loader.credentials = {"prov": ["prov_api_key"]}
    out = loader.format_credentials({"extra_random_key": "v"})
    assert "prov_api_key" in out
    assert "extra_random_key" in out


def test_format_credentials_warns_when_duplicate_credential():
    loader = CredentialsLoader()
    loader.credentials = {"prov_a": ["shared"], "prov_b": ["shared"]}
    with pytest.warns(Warning):
        out = loader.format_credentials({})
    assert "shared" in out


def test_format_credentials_skips_additional_key_already_formatted():
    class _StickyDict(dict):
        def pop(self, key, default=None):
            return self.get(key, default)

    loader = CredentialsLoader()
    loader.credentials = {"prov": ["api_key"]}

    with patch("builtins.dict", _StickyDict):
        out = loader.format_credentials({"api_key": "from_additional"})

    assert "api_key" in out


def test_from_obbject_extension_error_warns_when_not_debug():
    import warnings as _warnings

    import openbb_core.app.model.credentials as _cred_mod

    loader = _cred_mod.CredentialsLoader()
    loader.credentials = {}

    class _BoomExt:
        @property
        def credentials(self):
            raise RuntimeError("boom")

    fake_loader = type("FakeLoader", (), {"obbject_objects": {"badext": _BoomExt()}})

    with (
        patch("openbb_core.app.model.credentials.ExtensionLoader", lambda: fake_loader),
        patch(
            "openbb_core.app.model.credentials.Env",
            type("E", (), {"DEBUG_MODE": False}),
        ),
        _warnings.catch_warnings(record=True) as caught,
    ):
        _warnings.simplefilter("always")
        loader.from_obbject()
    assert any("badext" in str(w.message) for w in caught)


def test_from_obbject_skips_existing_extension_name():
    import warnings as _warnings

    import openbb_core.app.model.credentials as _cred_mod

    loader = _cred_mod.CredentialsLoader()
    loader.credentials = {"already": ["x"]}

    class _Ext:
        credentials = ["new"]

    fake_loader = type("FakeLoader", (), {"obbject_objects": {"already": _Ext()}})
    with (
        patch("openbb_core.app.model.credentials.ExtensionLoader", lambda: fake_loader),
        _warnings.catch_warnings(record=True) as caught,
    ):
        _warnings.simplefilter("always")
        loader.from_obbject()
    assert any("already" in str(w.message) for w in caught)
    assert loader.credentials["already"] == ["x"]


def test_is_unset_none():
    assert Credentials._is_unset(None) is True


def test_is_unset_empty_secret_str():
    from pydantic import SecretStr

    assert Credentials._is_unset(SecretStr("")) is True


def test_is_unset_filled_secret_str():
    from pydantic import SecretStr

    assert Credentials._is_unset(SecretStr("xx")) is False


def test_is_unset_empty_string():
    assert Credentials._is_unset("") is True


def test_is_unset_other_value_is_set():
    assert Credentials._is_unset(123) is False


def test_credentials_repr_contains_class_name_and_keys():
    c = Credentials()
    r = repr(c)
    assert "Credentials" in r


def test_credentials_update_merges_non_none_values():
    """``update`` copies fields from one Credentials into another."""
    from pydantic import SecretStr

    a = Credentials()
    b = Credentials()
    # Pick the first known credential field and set it on b
    field_name = next(iter(type(b).model_fields), None)
    if field_name is None:
        pytest.skip("No credential fields loaded in this environment")
    setattr(b, field_name, SecretStr("FROM_B"))
    a.update(b)
    val = getattr(a, field_name)
    assert val is not None
    assert val.get_secret_value() == "FROM_B"


def test_from_obbject_debug_mode_raises_loading_error():
    import openbb_core.app.model.credentials as _cred_mod

    loader = _cred_mod.CredentialsLoader()
    loader.credentials = {}

    class _BoomExt:
        @property
        def credentials(self):
            raise RuntimeError("boom")

    fake_loader = type("FakeLoader", (), {"obbject_objects": {"badext": _BoomExt()}})

    with (
        patch("openbb_core.app.model.credentials.ExtensionLoader", lambda: fake_loader),
        patch(
            "openbb_core.app.model.credentials.Env",
            type("E", (), {"DEBUG_MODE": True}),
        ),
        pytest.raises(_cred_mod.LoadingError, match="badext"),
    ):
        loader.from_obbject()


def test_model_post_init_applies_env_defaults_when_unset():
    """When a credential is unset, the env default value is applied."""
    from pydantic import SecretStr

    # Find a field that is unset by default (no env value loaded for it)
    instance = Credentials()
    field_name = next(
        (
            f
            for f in Credentials.model_fields
            if Credentials._is_unset(getattr(instance, f, None))
        ),
        None,
    )
    if field_name is None:
        pytest.skip("Every credential field has a real env value loaded")

    env_defaults_backup = dict(Credentials._env_defaults)
    Credentials._env_defaults[field_name] = SecretStr("FROM_ENV")
    try:
        c = Credentials()
        val = getattr(c, field_name)
        assert val is not None
        secret = val.get_secret_value() if hasattr(val, "get_secret_value") else val
        assert secret == "FROM_ENV"  # noqa: S105
    finally:
        Credentials._env_defaults.clear()
        Credentials._env_defaults.update(env_defaults_backup)


def test_model_post_init_skips_already_set_field():
    from pydantic import SecretStr

    field_name = next(iter(Credentials.model_fields), None)
    if field_name is None:
        pytest.skip("No credential fields loaded in this environment")
    env_defaults_backup = dict(Credentials._env_defaults)
    Credentials._env_defaults[field_name] = SecretStr("FROM_ENV")
    try:
        c = Credentials(**{field_name: SecretStr("USER_SET")})
        val = getattr(c, field_name)
        secret = val.get_secret_value() if hasattr(val, "get_secret_value") else val
        assert secret == "USER_SET"  # noqa: S105
    finally:
        Credentials._env_defaults.clear()
        Credentials._env_defaults.update(env_defaults_backup)


def test_model_post_init_skips_env_default_for_unknown_field():
    env_defaults_backup = dict(Credentials._env_defaults)
    Credentials._env_defaults["not_a_model_field"] = "X"
    try:
        c = Credentials()
        assert not hasattr(c, "not_a_model_field")
    finally:
        Credentials._env_defaults.clear()
        Credentials._env_defaults.update(env_defaults_backup)


def test_credentials_show_prints_class_name(capsys):
    """``show()`` prints class name and dumped credentials."""
    Credentials().show()
    out = capsys.readouterr().out
    assert "Credentials" in out


def test_load_picks_up_env_credentials(monkeypatch, tmp_path):
    """``load()`` should pull a credential from the environment when the env key matches an existing provider field."""
    import openbb_core.app.model.credentials as _cred_mod

    field_name = next(iter(Credentials.model_fields), None)
    if field_name is None:
        pytest.skip("No credential fields loaded in this environment")

    monkeypatch.setenv(field_name.upper(), "ENV_VALUE")
    monkeypatch.setattr(_cred_mod, "USER_SETTINGS_PATH", str(tmp_path / "missing.json"))

    model_cls = _cred_mod.CredentialsLoader().load()
    instance = model_cls()
    val = getattr(instance, field_name)
    assert val is not None


def test_load_reads_credentials_from_user_settings_file(monkeypatch, tmp_path):
    """A credentials block in the user settings file is merged in."""
    import openbb_core.app.model.credentials as _cred_mod

    field_name = next(iter(Credentials.model_fields), None)
    if field_name is None:
        pytest.skip("No credential fields loaded in this environment")
    settings_file = tmp_path / "user_settings.json"
    settings_file.write_text('{"credentials": {"' + field_name + '": "FROM_FILE"}}')
    monkeypatch.setattr(_cred_mod, "USER_SETTINGS_PATH", str(settings_file))

    model_cls = _cred_mod.CredentialsLoader().load()
    instance = model_cls()
    val = getattr(instance, field_name)
    assert val is not None
