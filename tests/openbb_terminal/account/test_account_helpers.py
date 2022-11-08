from openbb_terminal.account.account_helpers import clean_keys_dict


def test_clean_keys_dict():
    start = {"hello": None, "goodbye": 5}
    new_dict = clean_keys_dict(start)
    assert new_dict == {"hello": "", "goodbye": 5}
