"""Decorators"""
__docformat__ = "numpy"
import functools
import logging
import difflib

from gamestonk_terminal import feature_flags as gtff
import gamestonk_terminal.config_terminal as cfg
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import get_flair

logger = logging.getLogger(__name__)


def try_except(f):
    """Adds a try except block if the user is not in development mode

    Parameters
    -------
    f: function
        The function to be wrapped
    """
    # pylint: disable=inconsistent-return-statements
    @functools.wraps(f)
    def inner(*args, **kwargs):
        if cfg.DEBUG_MODE:
            return f(*args, **kwargs)
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.exception("%s", type(e).__name__)
            return []

    return inner


def menu_decorator(path: str, controller_class, dynamic_completer=None):
    """
    This decortator allows users to create context menus with three lines of code.

    path: str
        The path to display
    controller_class: class
        The context class to use
    dynamic_completer: function
        A function that defines dynamic autofill options for users
    """

    def decorator(_):
        def wrapper(*args, **kwargs):
            controller = controller_class(*args, **kwargs)
            an_input = "HELP_ME"

            while True:
                # There is a command in the queue
                if controller.queue and len(controller.queue) > 0:
                    # If the command is quitting the menu we want to return in here
                    if controller.queue[0] in ("q", "..", "quit"):
                        print("")
                        if len(controller.queue) > 1:
                            return controller.queue[1:]
                        return []

                    # Consume 1 element from the queue
                    an_input = controller.queue[0]
                    controller.queue = controller.queue[1:]

                    # Print location because this was an instruction and we want user to know the action
                    if (
                        an_input
                        and an_input.split(" ")[0] in controller.CHOICES_COMMANDS
                    ):
                        print(f"{get_flair()} {path} $ {an_input}")

                # Get input command from user
                else:
                    # Display help menu when entering on this menu from a level above
                    if an_input == "HELP_ME":
                        controller.print_help()

                    # Get input from user using auto-completion
                    if session and gtff.USE_PROMPT_TOOLKIT:
                        # Possible arguments is not yet finalized
                        if not controller.completer:
                            # Complete dynamic arguments that change at each iteration
                            controller.completer = dynamic_completer(controller)
                        try:
                            an_input = session.prompt(
                                f"{get_flair()} {path} $ ",
                                completer=controller.completer,
                                search_ignore_case=True,
                            )
                        except KeyboardInterrupt:
                            # Exit in case of keyboard interrupt
                            an_input = "exit"
                    # Get input from user without auto-completion
                    else:
                        an_input = input(f"{get_flair()} {path} $ ")

                try:
                    # Process the input command
                    controller.queue = controller.switch(an_input)

                except SystemExit:
                    print(
                        f"\nThe command '{an_input}' doesn't exist on the {path[:-1]} menu.",
                        end="",
                    )
                    similar_cmd = difflib.get_close_matches(
                        an_input.split(" ")[0] if " " in an_input else an_input,
                        controller.CHOICES,
                        n=1,
                        cutoff=0.7,
                    )
                    if similar_cmd:
                        if " " in an_input:
                            candidate_input = (
                                f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                            )
                            if candidate_input == an_input:
                                an_input = ""
                                controller.queue = []
                                print("\n")
                                continue
                            an_input = candidate_input
                        else:
                            an_input = similar_cmd[0]

                        print(f" Replacing by '{an_input}'.")
                        controller.queue.insert(0, an_input)
                    else:
                        print("\n")

        return wrapper

    return decorator
