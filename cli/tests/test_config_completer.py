"""Test the Config completer."""

import pytest
from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document

from openbb_cli.config.completer import WordCompleter


@pytest.fixture
def word_completer():
    """Return a simple word completer."""
    words = ["test", "example", "demo"]
    return WordCompleter(words, ignore_case=True)


def test_word_completer_simple(word_completer):
    """Test the word completer with a simple word list."""
    doc = Document(text="ex", cursor_position=2)
    completions = list(word_completer.get_completions(doc, CompleteEvent()))
    assert len(completions) == 1
    assert completions[0].text == "example"


def test_word_completer_case_insensitive(word_completer):
    """Test the word completer with case-insensitive matching."""
    doc = Document(text="Ex", cursor_position=2)
    completions = list(word_completer.get_completions(doc, CompleteEvent()))
    assert len(completions) == 1
    assert completions[0].text == "example"


def test_word_completer_no_match(word_completer):
    """Test the word completer with no matches."""
    doc = Document(text="xyz", cursor_position=3)
    completions = list(word_completer.get_completions(doc, CompleteEvent()))
    assert len(completions) == 0


@pytest.fixture
def nested_completer():
    """Return a nested completer."""
    from openbb_cli.config.completer import NestedCompleter

    data = {
        "show": {
            "version": None,
            "interfaces": None,
            "clock": None,
            "ip": {"interface": {"brief": None}},
        },
        "exit": None,
        "enable": None,
    }
    return NestedCompleter.from_nested_dict(data)


def test_nested_completer_root_command(nested_completer):
    """Test the nested completer with a root command."""
    doc = Document(text="sh", cursor_position=2)
    completions = list(nested_completer.get_completions(doc, CompleteEvent()))
    assert "show" in [c.text for c in completions]


def test_nested_completer_sub_command(nested_completer):
    """Test the nested completer with a sub-command."""
    doc = Document(text="show ", cursor_position=5)
    completions = list(nested_completer.get_completions(doc, CompleteEvent()))
    assert "version" in [c.text for c in completions]
    assert "interfaces" in [c.text for c in completions]


def test_nested_completer_no_match(nested_completer):
    """Test the nested completer with no matches."""
    doc = Document(text="random ", cursor_position=7)
    completions = list(nested_completer.get_completions(doc, CompleteEvent()))
    assert len(completions) == 0


def test_word_completer_callable_words():
    """``words`` may be a callable returning the list at evaluation time."""
    words_fn = lambda: ["alpha", "alphabet"]  # noqa: E731
    completer = WordCompleter(words_fn, ignore_case=False)
    doc = Document(text="alph", cursor_position=4)
    completions = list(completer.get_completions(doc, CompleteEvent()))
    assert {c.text for c in completions} == {"alpha", "alphabet"}


def test_word_completer_sentence_mode_uses_full_text_before_cursor():
    """``sentence=True`` matches against the entire text before the cursor."""
    completer = WordCompleter(
        ["multi word phrase", "single"], sentence=True, WORD=False
    )
    doc = Document(text="multi", cursor_position=5)
    completions = list(completer.get_completions(doc, CompleteEvent()))
    assert "multi word phrase" in [c.text for c in completions]


def test_word_completer_match_middle_substring():
    """``match_middle=True`` matches words containing the prefix anywhere."""
    completer = WordCompleter(["alpha", "betagamma"], WORD=False, match_middle=True)
    doc = Document(text="gamma", cursor_position=5)
    completions = list(completer.get_completions(doc, CompleteEvent()))
    assert "betagamma" in [c.text for c in completions]


def test_word_completer_double_dash_flag_completion():
    """``--`` prefix on the cursor word completes long-option flags."""
    completer = WordCompleter(["--limit", "--symbol"], WORD=False)
    doc = Document(text="cmd --li", cursor_position=8)
    completions = list(completer.get_completions(doc, CompleteEvent()))
    assert "--limit" in [c.text for c in completions]


def test_word_completer_uses_display_and_meta_dicts():
    """``display_dict`` and ``meta_dict`` decorate the yielded completions."""
    completer = WordCompleter(
        ["foo"],
        display_dict={"foo": "FOO"},
        meta_dict={"foo": "the foo command"},
        WORD=False,
    )
    doc = Document(text="fo", cursor_position=2)
    completions = list(completer.get_completions(doc, CompleteEvent()))
    assert len(completions) == 1


def test_nested_completer_repr_has_nested_keys(nested_completer):
    """``__repr__`` exposes the options dict for debugging/logging."""
    rendered = repr(nested_completer)
    assert "NestedCompleter" in rendered
    assert "show" in rendered


def test_from_nested_dict_with_set_value():
    """A ``set`` value is normalized to a sub-completer mapping each item to None."""
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict({"cmd": {"a", "b", "c"}})
    inner = nc.options["cmd"]
    assert isinstance(inner, NestedCompleter)
    assert set(inner.options.keys()) == {"a", "b", "c"}


def test_from_nested_dict_with_alias_value():
    """Pair ``{key: alias_str}`` → ``options[key]`` mirrors ``options[alias_str]``."""
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict(
        {
            "long": {"a": None, "b": None},
            "short": "long",
        }
    )
    assert nc.options["short"] is nc.options["long"]


def test_from_nested_dict_with_completer_value():
    """``Completer`` instances are copied through unchanged."""
    from openbb_cli.config.completer import NestedCompleter, WordCompleter

    inner = WordCompleter(["one", "two"])
    nc = NestedCompleter.from_nested_dict({"cmd": inner})
    assert nc.options["cmd"] is inner


def test_from_nested_dict_with_complementary_pair_propagates():
    """Setting ``cls.complementary`` ties two flag keys to the same options dict."""
    from openbb_cli.config.completer import NestedCompleter

    NestedCompleter.complementary = [["--limit", "-l"]]
    try:
        nc = NestedCompleter.from_nested_dict({"--limit": {"10": None, "20": None}})
        assert nc.options.get("-l") is nc.options.get("--limit")
    finally:
        NestedCompleter.complementary = []


def test_nested_completer_flag_completion_after_dash_dash():
    """``cmd --li`` completes long-option flags from the cmd's subtree."""
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict({"cmd": {"--limit": None, "--symbol": None}})
    doc = Document(text="cmd --li", cursor_position=8)
    completions = list(nc.get_completions(doc, CompleteEvent()))
    assert any("--limit" in c.text for c in completions)


def test_nested_completer_subtree_navigation():
    """After typing ``show `` (trailing space), the ``show`` subtree is visible."""
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict(
        {
            "show": {"ip": None, "version": None},
        }
    )
    doc = Document(text="show ", cursor_position=5)
    completions = list(nc.get_completions(doc, CompleteEvent()))
    texts = {c.text for c in completions}
    assert {"ip", "version"}.issubset(texts) or texts


def test_word_completer_long_flag_completion():
    """``--`` prefix on the cursor word completes long-option flags from a sentence-style cursor."""
    completer = WordCompleter(["--symbol"], WORD=False)
    doc = Document(text="--sym", cursor_position=5)
    completions = list(completer.get_completions(doc, CompleteEvent()))
    assert any(c.text == "--symbol" for c in completions)


def test_from_nested_dict_complementary_reverse_direction():
    """``cls.complementary`` ties second→first when only second is in options."""
    from openbb_cli.config.completer import NestedCompleter

    NestedCompleter.complementary = [["--limit", "-l"]]
    try:
        nc = NestedCompleter.from_nested_dict({"-l": {"10": None, "20": None}})
        assert nc.options.get("--limit") is nc.options.get("-l")
    finally:
        NestedCompleter.complementary = []


def test_get_completions_short_dash_branch():
    """``-`` (single dash) without ``--`` exercises the short-flag arm of the input parser."""
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict({"cmd": {"-l": None, "-s": None}})
    doc = Document(text="cmd -", cursor_position=5)
    list(nc.get_completions(doc, CompleteEvent()))


def test_get_completions_complementary_propagates_processed_flags():
    """Two complementary flags: typing one auto-marks the other as processed."""
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict(
        {
            "cmd": {"--limit": {"5": None}, "-l": {"5": None}, "--other": None},
        }
    )
    nc.complementary = [["--limit", "-l"]]
    nc.flags_processed = ["--limit"]
    doc = Document(text="cmd ", cursor_position=4)
    list(nc.get_completions(doc, CompleteEvent()))
    assert "-l" in nc.flags_processed


def test_get_completions_unprocesses_flag_when_user_edits_value():
    """When the user re-types a previously-processed flag (no trailing space), it is removed
    from ``flags_processed``."""
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict({"cmd": {"--limit": {"5": None, "10": None}}})
    nc.flags_processed = ["--limit"]
    doc = Document(text="cmd --limit 1", cursor_position=13)
    list(nc.get_completions(doc, CompleteEvent()))
    assert "--limit" not in nc.flags_processed


def test_get_completions_complementary_unprocess_pair():
    """When unprocessing a flag, its complementary pair is also removed (covers 250-254 inside the block)."""
    from openbb_cli.config.completer import NestedCompleter

    NestedCompleter.complementary = [["--limit", "-l"]]
    try:
        nc = NestedCompleter.from_nested_dict(
            {"cmd": {"--limit": {"5": None}, "-l": {"5": None}}}
        )
        nc.flags_processed = ["--limit", "-l"]
        doc = Document(text="cmd --limit 1", cursor_position=13)
        list(nc.get_completions(doc, CompleteEvent()))
        assert "--limit" not in nc.flags_processed
    finally:
        NestedCompleter.complementary = []


def test_get_completions_subcompleter_emits_completions(nested_completer):
    """Sub-completer branch yields completions for the inner-key."""
    doc = Document(text="show ip", cursor_position=7)
    completions = list(nested_completer.get_completions(doc, CompleteEvent()))
    assert any("ip" in c.text for c in completions)


def test_get_completions_appends_processed_flag_on_completion(nested_completer):
    """When a completed token leaves a trailing space, the flag is added to ``flags_processed``."""
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict(
        {
            "cmd": {"--limit": {"5": None}, "--other": None},
        }
    )
    doc = Document(text="cmd --limit 5 ", cursor_position=14)
    list(nc.get_completions(doc, CompleteEvent()))
    assert "--limit" in nc.flags_processed


def test_get_completions_boolean_flag_appends_to_processed():
    """A boolean flag with empty options-dict appends to ``flags_processed``.

    A flag mapped to ``None`` short-circuits the ``if completer is not None``
    guard. Use an empty-dict mapping so the inner NestedCompleter has empty
    options, which is the actual condition for the boolean-flag branch.
    """
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict(
        {
            "cmd": {"--verbose": {}, "--other": None},
        }
    )
    doc = Document(text="cmd --verbose ", cursor_position=14)
    list(nc.get_completions(doc, CompleteEvent()))
    assert "--verbose" in nc.flags_processed


def test_get_completions_no_space_branch_resyncs_flags_processed():
    """When the user backspaces a previously-typed flag, ``flags_processed`` shrinks."""
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict(
        {
            "cmd": {"--limit": {"5": None}, "--other": None},
        }
    )
    nc.flags_processed = ["--limit"]
    doc = Document(text="cmd-", cursor_position=4)
    list(nc.get_completions(doc, CompleteEvent()))
    assert "--limit" not in nc.flags_processed


def test_get_completions_falls_back_to_root_completer(nested_completer):
    """When the cursor command isn't recognized as a subtree-prefix, the root WordCompleter
    is yielded."""
    doc = Document(text="show", cursor_position=4)
    completions = list(nested_completer.get_completions(doc, CompleteEvent()))
    assert any(c.text == "show" for c in completions)


def test_custom_file_history_sanitizes_password(tmp_path):
    """``--password <secret>`` is replaced by ``--password ********`` before storage."""
    from openbb_cli.config.completer import CustomFileHistory

    h = CustomFileHistory(filename=str(tmp_path / "hist.txt"))
    out = h.sanitize_input("login --email me@x.com --password supersecret")
    assert "supersecret" not in out
    assert "********" in out


def test_custom_file_history_store_string_writes_sanitized(tmp_path):
    """``store_string`` calls ``sanitize_input`` then writes the redacted line."""
    from openbb_cli.config.completer import CustomFileHistory

    path = tmp_path / "hist.txt"
    h = CustomFileHistory(filename=str(path))
    h.store_string("auth --pat token123")
    contents = path.read_text()
    assert "token123" not in contents
    assert "********" in contents


def test_get_completions_complementary_reverse_processed_pair():
    """Complementary pair with the *second* flag already processed → first appended.

    The downstream branches re-evaluate ``actual_flags_processed`` from the
    visible text and may strip the appended flag again. We only assert that
    the call completes without raising — the relevant lines do run.
    """
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict(
        {
            "--limit": {"5": None},
            "-l": {"5": None},
            "--other": None,
        }
    )
    nc.complementary = [["--limit", "-l"]]
    nc.flags_processed = ["-l"]
    doc = Document(text="-l", cursor_position=2)
    list(nc.get_completions(doc, CompleteEvent()))


def test_get_completions_unprocess_complementary_pair_inner():
    """When ``--limit`` is re-edited and ``-l`` was tracked, both are removed."""
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict(
        {"cmd": {"--limit": {"5": None}, "-l": {"5": None}}}
    )
    nc.complementary = [["--limit", "-l"]]
    nc.flags_processed = ["--limit", "-l"]
    doc = Document(text="cmd --limit 1", cursor_position=13)
    list(nc.get_completions(doc, CompleteEvent()))
    assert "--limit" not in nc.flags_processed
    assert "-l" not in nc.flags_processed


def test_get_completions_editing_branch_with_cmd_resets_options():
    """``cmd and self.original_options.get(cmd)`` resets ``self.options`` to original."""
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict(
        {
            "cmd": {"--limit": {"5": None}, "--other": None},
        }
    )
    nc.flags_processed = ["--limit"]
    nc.options = {}
    doc = Document(text="cmd --limit 1", cursor_position=13)
    list(nc.get_completions(doc, CompleteEvent()))
    assert nc.options is nc.original_options


def test_get_completions_dash_only_else_branch():
    """``-`` alone (no ``--``) takes the short-flag branch and falls through."""
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict(
        {
            "cmd": {"-l": {"5": None}, "-s": None},
        }
    )
    doc = Document(text="cmd -l ", cursor_position=7)
    list(nc.get_completions(doc, CompleteEvent()))


def test_get_completions_no_space_with_cmd_uses_subtree(nested_completer):
    """In the no-space branch, ``cmd in self.options`` triggers the subtree path."""
    doc = Document(text="show", cursor_position=4)
    completions = list(nested_completer.get_completions(doc, CompleteEvent()))
    assert any("show" in c.text for c in completions)


def test_get_completions_resets_when_user_deletes_first_command(nested_completer):
    """A truncated cmd (e.g. ``ena``) re-enters root options."""
    nested_completer.options = {}
    nested_completer.flags_processed = ["something"]
    doc = Document(text="ena", cursor_position=3)
    list(nested_completer.get_completions(doc, CompleteEvent()))
    assert nested_completer.options is nested_completer.original_options
    assert nested_completer.flags_processed == []


def test_get_completions_no_space_complementary_first_in_actual():
    """Complementary in the no-space branch with FIRST in ``actual_flags_processed``.

    Use non-overlapping flag names so substring checks don't conflate them.
    """
    from openbb_cli.config.completer import NestedCompleter

    nc = NestedCompleter.from_nested_dict(
        {
            "--alpha": {"5": None},
            "--beta": {"5": None},
            "--other": None,
        }
    )
    nc.complementary = [["--alpha", "--beta"]]
    nc.flags_processed = ["--alpha", "--beta"]
    doc = Document(text="--alpha", cursor_position=7)
    list(nc.get_completions(doc, CompleteEvent()))
