"""Nested completer for completion of OpenBB hierarchical data structures."""

from collections.abc import Callable, Iterable, Mapping
from re import Pattern
from typing import (
    Any,
)

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.history import FileHistory

NestedDict = Mapping[str, Any | set[str] | None | Completer]


class WordCompleter(Completer):
    """Simple autocompletion on a list of words.

    Parameters
    ----------
    words : list[str] or callable
        List of words or a callable returning a list of words.
    ignore_case : bool
        When ``True``, complete case-insensitively.
    meta_dict : Mapping[str, AnyFormattedText], optional
        Maps words to their meta-text (strings or formatted text).
    WORD : bool
        When ``True``, use WORD characters.
    sentence : bool
        When ``True``, don't complete by comparing the word before the
        cursor, but by comparing all the text before the cursor. In this
        case, the list of words is just a list of strings, where each
        string can contain spaces. Cannot be used together with ``WORD``.
    match_middle : bool
        When ``True``, match not only the start of the word but also its
        middle.
    pattern : re.Pattern[str], optional
        Compiled regex for finding the word before the cursor to complete.
        When supplied, used instead of the default ``document._FIND_WORD_RE``.
    """

    def __init__(
        self,
        words: list[str] | Callable[[], list[str]],
        ignore_case: bool = False,
        display_dict: Mapping[str, AnyFormattedText] | None = None,
        meta_dict: Mapping[str, AnyFormattedText] | None = None,
        WORD: bool = True,
        sentence: bool = False,
        match_middle: bool = False,
        pattern: Pattern[str] | None = None,
    ) -> None:
        """Initialize the WordCompleter."""
        assert not (WORD and sentence)  # noqa: S101

        self.words = words
        self.ignore_case = ignore_case
        self.display_dict = display_dict or {}
        self.meta_dict = meta_dict or {}
        self.WORD = WORD
        self.sentence = sentence
        self.match_middle = match_middle
        self.pattern = pattern

    def get_completions(  # ty: ignore[invalid-method-override]
        self,
        document: Document,
        _complete_event: CompleteEvent,
    ) -> Iterable[Completion]:
        """Get completions."""
        words = self.words
        if callable(words):
            words = words()  # ty: ignore[call-top-callable]

        if self.sentence:
            word_before_cursor = document.text_before_cursor
        else:
            word_before_cursor = document.get_word_before_cursor(
                WORD=self.WORD, pattern=self.pattern
            )
            if (
                "--" in document.text_before_cursor
                and document.text_before_cursor.rfind(" --")
                >= document.text_before_cursor.rfind(" -")
            ):
                word_before_cursor = f"--{document.text_before_cursor.split('--')[-1]}"
            elif (  # pragma: no cover
                f"--{word_before_cursor}" == document.text_before_cursor
            ):
                word_before_cursor = document.text_before_cursor

        if self.ignore_case:
            word_before_cursor = word_before_cursor.lower()

        def word_matches(word: str) -> bool:
            """Set True when the word before the cursor matches."""
            if self.ignore_case:
                word = word.lower()

            if self.match_middle:
                return word_before_cursor in word
            return word.startswith(word_before_cursor)

        for a in words:
            if word_matches(a):
                display = self.display_dict.get(a, a)
                display_meta = self.meta_dict.get(a, "")
                yield Completion(
                    text=a,
                    start_position=-len(word_before_cursor),
                    display=display,
                    display_meta=display_meta,
                )


class NestedCompleter(Completer):
    """Completer wrapping several others, dispatching by the input's first word.

    By combining multiple `NestedCompleter` instances, we can achieve multiple
    hierarchical levels of autocompletion. This is useful when `WordCompleter`
    is not sufficient.

    If you need multiple levels, check out the `from_nested_dict` classmethod.
    """

    complementary: list = list()

    def __init__(
        self, options: dict[str, Completer | None], ignore_case: bool = True
    ) -> None:
        """Initialize the NestedCompleter."""
        self.flags_processed: list = list()
        self.original_options = options
        self.options = options
        self.ignore_case = ignore_case
        self.complementary = list()

    def __repr__(self) -> str:
        """Return string representation of NestedCompleter."""
        return f"NestedCompleter({self.options!r}, ignore_case={self.ignore_case!r})"

    @classmethod
    def from_nested_dict(cls, data: dict) -> "NestedCompleter":
        """Create a `NestedCompleter`.

        It starts from a nested dictionary data structure, like this:

        .. code::

            data = {
                'show': {
                    'version': None,
                    'interfaces': None,
                    'clock': None,
                    'ip': {'interface': {'brief'}}
                },
                'exit': None
                'enable': None
            }

        The value should be `None` if there is no further completion at some
        point. If all values in the dictionary are None, it is also possible to
        use a set instead.

        Values in this data structure can be a completers as well.
        """
        options: dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, Completer):
                options[key] = value
            elif isinstance(value, dict):
                options[key] = cls.from_nested_dict(value)
            elif isinstance(value, set):
                options[key] = cls.from_nested_dict({item: None for item in value})
            elif isinstance(key, str) and isinstance(value, str):
                options[key] = options[value]
            else:
                assert value is None  # noqa: S101
                options[key] = None

        for items in cls.complementary:
            if items[0] in options:
                options[items[1]] = options[items[0]]
            elif items[1] in options:
                options[items[0]] = options[items[1]]

        return cls(options)

    def get_completions(  # noqa: PLR0912
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """Get completions."""
        cmd = ""
        text = document.text_before_cursor.lstrip()
        if " " in text:
            cmd = text.split(" ")[0]
        if "-" in text:
            if text.rfind("--") == -1 or text.rfind("-") - 1 > text.rfind("--"):
                unprocessed_text = "-" + text.split("-")[-1]
            else:
                unprocessed_text = "--" + text.split("--")[-1]
        else:
            unprocessed_text = text
        stripped_len = len(document.text_before_cursor) - len(text)

        if self.complementary:
            for same_flags in self.complementary:
                if (
                    same_flags[0] in self.flags_processed
                    and same_flags[1] not in self.flags_processed
                ) or (
                    same_flags[1] in self.flags_processed
                    and same_flags[0] not in self.flags_processed
                ):
                    if same_flags[0] in self.flags_processed:
                        self.flags_processed.append(same_flags[1])
                    elif same_flags[1] in self.flags_processed:
                        self.flags_processed.append(same_flags[0])

                    if cmd:
                        self.options = {
                            k: self.original_options.get(cmd).options[k]  # ty: ignore[unresolved-attribute]
                            for k in self.original_options.get(cmd).options  # ty: ignore[unresolved-attribute]
                            if k not in self.flags_processed
                        }
                    else:
                        self.options = {
                            k: self.original_options[k]
                            for k in self.original_options
                            if k not in self.flags_processed
                        }

        if " " in unprocessed_text:
            first_term = unprocessed_text.split()[0]

            if unprocessed_text[-1] != " ":
                self.flags_processed = [
                    flag for flag in self.flags_processed if flag != first_term
                ]

                if self.complementary:
                    for same_flags in self.complementary:
                        if (
                            same_flags[0] in self.flags_processed
                            and same_flags[1] not in self.flags_processed
                        ) or (
                            same_flags[1] in self.flags_processed
                            and same_flags[0] not in self.flags_processed
                        ):
                            if (
                                same_flags[0] in self.flags_processed
                            ):  # pragma: no cover
                                self.flags_processed.remove(same_flags[0])
                            elif (
                                same_flags[1] in self.flags_processed
                            ):  # pragma: no cover
                                self.flags_processed.remove(same_flags[1])

                if cmd and self.original_options.get(cmd):
                    self.options = self.original_options
                else:  # pragma: no cover
                    self.options = {
                        k: self.original_options[k]
                        for k in self.original_options
                        if k not in self.flags_processed
                    }

            if "-" not in text:
                completer = self.options.get(first_term)
            elif cmd in self.options and self.options.get(cmd):
                completer = self.options.get(cmd).options.get(first_term)  # ty: ignore[unresolved-attribute]
            else:  # pragma: no cover
                completer = self.options.get(first_term)

            if completer is not None:
                remaining_text = unprocessed_text[len(first_term) :].lstrip()
                move_cursor = len(text) - len(remaining_text) + stripped_len

                new_document = Document(
                    remaining_text,
                    cursor_position=document.cursor_position - move_cursor,
                )

                if " " in new_document.text:
                    if (
                        new_document.text in [f"{opt} " for opt in self.options]
                        or unprocessed_text[-1] == " "
                    ):
                        self.flags_processed.append(first_term)
                        if cmd:
                            self.options = {
                                k: self.original_options.get(cmd).options[k]  # ty: ignore[unresolved-attribute]
                                for k in self.original_options.get(cmd).options  # ty: ignore[unresolved-attribute]
                                if k not in self.flags_processed
                            }
                        else:  # pragma: no cover
                            self.options = {
                                k: self.original_options[k]
                                for k in self.original_options
                                if k not in self.flags_processed
                            }

                elif not completer.options:  # ty: ignore[unresolved-attribute]
                    self.flags_processed.append(first_term)

                    if self.complementary:  # pragma: no cover
                        for same_flags in self.complementary:
                            if (
                                same_flags[0] in self.flags_processed
                                and same_flags[1] not in self.flags_processed
                            ) or (
                                same_flags[1] in self.flags_processed
                                and same_flags[0] not in self.flags_processed
                            ):
                                if same_flags[0] in self.flags_processed:
                                    self.flags_processed.append(same_flags[1])
                                elif same_flags[1] in self.flags_processed:
                                    self.flags_processed.append(same_flags[0])

                    if cmd:
                        self.options = {
                            k: self.original_options.get(cmd).options[k]  # ty: ignore[unresolved-attribute]
                            for k in self.original_options.get(cmd).options  # ty: ignore[unresolved-attribute]
                            if k not in self.flags_processed
                        }
                    else:  # pragma: no cover
                        self.options = {
                            k: self.original_options[k]
                            for k in self.original_options
                            if k not in self.flags_processed
                        }

                else:
                    yield from completer.get_completions(new_document, complete_event)

        else:
            if " " in text or "-" in text:
                actual_flags_processed = [
                    flag for flag in self.flags_processed if flag in text
                ]

                if self.complementary:
                    for same_flags in self.complementary:
                        if (
                            same_flags[0] in actual_flags_processed
                            and same_flags[1] not in actual_flags_processed
                        ) or (
                            same_flags[1] in actual_flags_processed
                            and same_flags[0] not in actual_flags_processed
                        ):
                            if same_flags[0] in actual_flags_processed:
                                actual_flags_processed.append(same_flags[1])
                            elif (
                                same_flags[1] in actual_flags_processed
                            ):  # pragma: no cover
                                actual_flags_processed.append(same_flags[0])

                if len(actual_flags_processed) < len(self.flags_processed):
                    self.flags_processed = actual_flags_processed
                    if cmd:  # pragma: no cover
                        self.options = {
                            k: self.original_options.get(cmd).options[k]  # ty: ignore[unresolved-attribute]
                            for k in self.original_options.get(cmd).options  # ty: ignore[unresolved-attribute]
                            if k not in self.flags_processed
                        }
                    else:
                        self.options = {
                            k: self.original_options[k]
                            for k in self.original_options
                            if k not in self.flags_processed
                        }

            command = self.options.get(cmd)
            options = command.options if command else {}  # ty: ignore[unresolved-attribute]
            command_options = [f"{cmd} {opt}" for opt in options]
            text_list = [text in val for val in command_options]
            if cmd and cmd in self.options and text_list:
                completer = WordCompleter(
                    list(self.options.get(cmd).options.keys()),  # ty: ignore[unresolved-attribute]
                    ignore_case=self.ignore_case,
                )
            elif bool([val for val in self.options if text in val]):
                completer = WordCompleter(
                    list(self.options.keys()), ignore_case=self.ignore_case
                )
            else:
                if bool([val for val in self.original_options if text in val]):
                    self.options = self.original_options
                    self.flags_processed = list()
                completer = WordCompleter(
                    list(self.options.keys()), ignore_case=self.ignore_case
                )

            yield from completer.get_completions(document, complete_event)


class CustomFileHistory(FileHistory):
    """Filtered file history."""

    def sanitize_input(self, string: str) -> str:
        """Sanitize sensitive information from the input string by parsing arguments."""
        keywords = ["--password", "--email", "--pat"]
        string_list = string.split(" ")

        for kw in keywords:
            if kw in string_list:
                index = string_list.index(kw)
                if len(string_list) > index + 1:
                    string_list[index + 1] = "********"

        result = " ".join(string_list)
        return result

    def store_string(self, string: str) -> None:
        """Store string in history."""
        string = self.sanitize_input(string)
        super().store_string(string)
