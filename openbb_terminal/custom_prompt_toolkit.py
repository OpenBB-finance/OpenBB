""" Nestedcompleter for completion of OpenBB hierarchical data structures. """
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Pattern,
    Set,
    Union,
)

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import AnyFormattedText

NestedDict = Mapping[str, Union[Any, Set[str], None, Completer]]

# pylint: disable=too-many-arguments,global-statement,too-many-branches,global-variable-not-assigned


class WordCompleter(Completer):
    """
    Simple autocompletion on a list of words.

    :param words: List of words or callable that returns a list of words.
    :param ignore_case: If True, case-insensitive completion.
    :param meta_dict: Optional dict mapping words to their meta-text. (This
        should map strings to strings or formatted text.)
    :param WORD: When True, use WORD characters.
    :param sentence: When True, don't complete by comparing the word before the
        cursor, but by comparing all the text before the cursor. In this case,
        the list of words is just a list of strings, where each string can
        contain spaces. (Can not be used together with the WORD option.)
    :param match_middle: When True, match not only the start, but also in the
                         middle of the word.
    :param pattern: Optional compiled regex for finding the word before
        the cursor to complete. When given, use this regex pattern instead of
        default one (see document._FIND_WORD_RE)
    """

    def __init__(
        self,
        words: Union[List[str], Callable[[], List[str]]],
        ignore_case: bool = False,
        display_dict: Optional[Mapping[str, AnyFormattedText]] = None,
        meta_dict: Optional[Mapping[str, AnyFormattedText]] = None,
        WORD: bool = True,
        sentence: bool = False,
        match_middle: bool = False,
        pattern: Optional[Pattern[str]] = None,
    ) -> None:
        assert not (WORD and sentence)  # noqa: S101

        self.words = words
        self.ignore_case = ignore_case
        self.display_dict = display_dict or {}
        self.meta_dict = meta_dict or {}
        self.WORD = WORD
        self.sentence = sentence
        self.match_middle = match_middle
        self.pattern = pattern

    def get_completions(
        self,
        document: Document,
        _complete_event: CompleteEvent,
    ) -> Iterable[Completion]:
        # Get list of words.
        words = self.words
        if callable(words):
            words = words()

        # Get word/text before cursor.
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
                word_before_cursor = f'--{document.text_before_cursor.split("--")[-1]}'
            elif f"--{word_before_cursor}" == document.text_before_cursor:
                word_before_cursor = document.text_before_cursor

        if self.ignore_case:
            word_before_cursor = word_before_cursor.lower()

        def word_matches(word: str) -> bool:
            """True when the word before the cursor matches."""
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
    """
    Completer which wraps around several other completers, and calls any the
    one that corresponds with the first word of the input.

    By combining multiple `NestedCompleter` instances, we can achieve multiple
    hierarchical levels of autocompletion. This is useful when `WordCompleter`
    is not sufficient.

    If you need multiple levels, check out the `from_nested_dict` classmethod.
    """

    complementary: List = list()

    def __init__(
        self, options: Dict[str, Optional[Completer]], ignore_case: bool = True
    ) -> None:
        self.flags_processed: List = list()
        self.original_options = options
        self.options = options
        self.ignore_case = ignore_case
        self.complementary = list()

    def __repr__(self) -> str:
        return f"NestedCompleter({self.options!r}, ignore_case={self.ignore_case!r})"

    @classmethod
    def from_nested_dict(cls, data: dict) -> "NestedCompleter":
        """
        Create a `NestedCompleter`, starting from a nested dictionary data
        structure, like this:

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
        options: Dict[str, Any] = {}
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
        # Split document.
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

        # Check if there are multiple flags for the same command
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
                            k: self.original_options.get(cmd).options[k]  # type: ignore
                            for k in self.original_options.get(cmd).options  # type: ignore
                            if k not in self.flags_processed
                        }
                    else:
                        self.options = {
                            k: self.original_options[k]
                            for k in self.original_options
                            if k not in self.flags_processed
                        }

        # If there is a space, check for the first term, and use a subcompleter.
        if " " in unprocessed_text:
            first_term = unprocessed_text.split()[0]

            # user is updating one of the values
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
                            if same_flags[0] in self.flags_processed:
                                self.flags_processed.remove(same_flags[0])
                            elif same_flags[1] in self.flags_processed:
                                self.flags_processed.remove(same_flags[1])

                if cmd and self.original_options.get(cmd):
                    self.options = self.original_options
                else:
                    self.options = {
                        k: self.original_options[k]
                        for k in self.original_options
                        if k not in self.flags_processed
                    }

            if "-" not in text:
                completer = self.options.get(first_term)
            elif cmd in self.options and self.options.get(cmd):
                completer = self.options.get(cmd).options.get(first_term)  # type: ignore
            else:
                completer = self.options.get(first_term)

            # If we have a sub completer, use this for the completions.
            if completer is not None:
                remaining_text = unprocessed_text[len(first_term) :].lstrip()
                move_cursor = len(text) - len(remaining_text) + stripped_len

                new_document = Document(
                    remaining_text,
                    cursor_position=document.cursor_position - move_cursor,
                )

                # Provides auto-completion but if user doesn't take it still keep going
                if " " in new_document.text:
                    if (
                        new_document.text in [f"{opt} " for opt in self.options]
                        or unprocessed_text[-1] == " "
                    ):
                        self.flags_processed.append(first_term)
                        if cmd:
                            self.options = {
                                k: self.original_options.get(cmd).options[k]  # type: ignore
                                for k in self.original_options.get(cmd).options  # type: ignore
                                if k not in self.flags_processed
                            }
                        else:
                            self.options = {
                                k: self.original_options[k]
                                for k in self.original_options
                                if k not in self.flags_processed
                            }

                # In case the users inputs a single boolean flag
                elif not completer.options:  # type: ignore
                    self.flags_processed.append(first_term)

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
                            k: self.original_options.get(cmd).options[k]  # type: ignore
                            for k in self.original_options.get(cmd).options  # type: ignore
                            if k not in self.flags_processed
                        }
                    else:
                        self.options = {
                            k: self.original_options[k]
                            for k in self.original_options
                            if k not in self.flags_processed
                        }

                else:
                    # This is a NestedCompleter
                    yield from completer.get_completions(new_document, complete_event)

        # No space in the input: behave exactly like `WordCompleter`.
        else:
            # check if the prompt has been updated in the meantime
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
                            elif same_flags[1] in actual_flags_processed:
                                actual_flags_processed.append(same_flags[0])

                if len(actual_flags_processed) < len(self.flags_processed):
                    self.flags_processed = actual_flags_processed
                    if cmd:
                        self.options = {
                            k: self.original_options.get(cmd).options[k]  # type: ignore
                            for k in self.original_options.get(cmd).options  # type: ignore
                            if k not in self.flags_processed
                        }
                    else:
                        self.options = {
                            k: self.original_options[k]
                            for k in self.original_options
                            if k not in self.flags_processed
                        }

            command = self.options.get(cmd)
            options = command.options if command else {}  # type: ignore
            command_options = [f"{cmd} {opt}" for opt in options]
            text_list = [text in val for val in command_options]
            if cmd and cmd in self.options and text_list:
                completer = WordCompleter(
                    list(self.options.get(cmd).options.keys()),  # type: ignore
                    ignore_case=self.ignore_case,
                )
            elif bool([val for val in self.options if text in val]):
                completer = WordCompleter(
                    list(self.options.keys()), ignore_case=self.ignore_case
                )
            else:
                # The user has delete part of the first command and we need to reset options
                if bool([val for val in self.original_options if text in val]):
                    self.options = self.original_options
                    self.flags_processed = list()
                completer = WordCompleter(
                    list(self.options.keys()), ignore_case=self.ignore_case
                )

            # This is a WordCompleter
            yield from completer.get_completions(document, complete_event)
