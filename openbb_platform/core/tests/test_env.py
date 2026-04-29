from openbb_core.env import Env


def test_str2bool_invalid_value_raises():
    try:
        Env.str2bool("maybe")
        assert False
    except ValueError as exc:
        assert "Failed to cast maybe to bool" in str(exc)
