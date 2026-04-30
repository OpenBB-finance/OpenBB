from openbb_core.env import Env


def test_str2bool_invalid_value_raises():
    try:
        Env.str2bool("maybe")
        assert False
    except ValueError as exc:
        assert "Failed to cast maybe to bool" in str(exc)


def test_str2bool_false_value():
    assert Env.str2bool("false") is False


def test_auto_build_property_uses_env_value():
    env = Env()
    original = env._environ.copy()
    try:
        env._environ["OPENBB_AUTO_BUILD"] = "true"
        assert env.AUTO_BUILD is True
    finally:
        env._environ = original
