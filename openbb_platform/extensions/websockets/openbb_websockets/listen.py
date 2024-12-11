"""Convenience tool for listening to raw broadcast streams outside of the main application thread."""


class Listener:
    """WebSocket broadcast listener. Not intended to be initialized directly, use the 'listen' function."""

    def __init__(self, **kwargs):
        """Initialize the Listener. All keyword arguments are passed directly to websockets.connect."""

        self.loop = None
        self.websocket = None
        self.current_task = None
        self.logger = None
        self.kwargs: dict = {}
        if kwargs:
            self.kwargs = kwargs

    async def listen(  # noqa: PLR0915  # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        self, url, **kwargs
    ):
        """Listen for WebSocket messages."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import json
        import websockets
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import UnauthorizedError
        from openbb_websockets.helpers import clean_message, get_logger
        from websockets.exceptions import InvalidStatusCode

        kwargs = kwargs or {}

        if self.kwargs:
            for k, v in self.kwargs.items():
                if k not in kwargs:
                    kwargs[k] = v

        self.logger = get_logger(url)
        url = url.replace("http", "ws")

        if url.startswith("localhost"):
            url = url.replace("localhost", "ws://localhost")

        if url[0].isdigit():
            url = f"ws://{url}"

        try:
            while True:
                try:
                    async with websockets.connect(url, **kwargs) as websocket:
                        self.websocket = websocket
                        url = clean_message(url)
                        msg = f"\nListening for messages from {clean_message(url)}"
                        self.logger.info(msg)
                        for handler in self.logger.handlers:
                            handler.flush()
                        async for message in websocket:
                            if (
                                isinstance(message, str)
                                and "Invalid authentication token" in message
                            ):
                                raise UnauthorizedError(message)
                            self.logger.info(json.loads(message))
                            for handler in self.logger.handlers:
                                handler.flush()
                except UnauthorizedError as error:
                    self.logger.error(error)
                    break
                except (KeyboardInterrupt, asyncio.CancelledError):
                    self.logger.info("Disconnected from server.")
                    break
                except (
                    websockets.ConnectionClosedError,
                    asyncio.IncompleteReadError,
                ):
                    msg = f"The process hosting {clean_message(url)} was terminated."
                    self.logger.error(msg)
                    break
                except websockets.exceptions.InvalidURI as error:
                    msg = f"Invalid URI -> {error}"
                    self.logger.error(msg)
                    break
                except InvalidStatusCode as error:
                    msg = f"Invalid status code -> {error}"
                    self.logger.error(msg)
                    break
                except OSError as error:
                    if "Multiple exceptions" in str(error):
                        err = str(error).split("Multiple exceptions:")[1].strip()
                        err = err.split("[")[-1].strip().replace("]", ":")
                        msg = f"An error occurred while attempting to connect to: {clean_message(url)} -> {err}"
                        self.logger.error(msg)
                    else:
                        msg = f"An error occurred while attempting to connect to: {clean_message(url)} -> {error}"
                        self.logger.error(msg)
                    break
        except Exception as error:  # pylint: disable=broad-except
            msg = f"Unexpected error -> {error.__class__.__name__}: {error}"
            self.logger.error(msg)
            raise OpenBBError(error) from error
        finally:
            if self.websocket:
                await self.websocket.close()

    def stop(self):
        """Stop the listener."""
        if self.current_task:
            self.current_task.cancel()
            self.loop.run_until_complete(self.current_task)  # type: ignore
        if self.websocket:
            self.loop.run_until_complete(self.websocket.close())  # type: ignore
        if not self.loop.is_closed():  # type: ignore
            self.loop.stop()  # type: ignore

    async def start_listening(self, url, **kwargs):
        """Start listening for WebSocket messages."""
        # pylint: disable=import-outside-toplevel
        import asyncio
        import contextlib

        self.current_task = self.loop.create_task(self.listen(url, **kwargs))  # type: ignore
        with contextlib.suppress(asyncio.CancelledError):
            await self.current_task

    def run(self, url, **kwargs):
        """Run the listener."""
        # pylint: disable=import-outside-toplevel
        import asyncio

        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.start_listening(url, **kwargs))
        except KeyboardInterrupt:
            self.logger.info("\nWebSocket listener terminated.")  # type: ignore
        finally:
            self.stop()


def listen(url, **kwargs):
    """Listen for WebSocket messages from a given URL. This function is blocking.

    Parameters
    ----------
    url : str
        The WebSocket URL to connect to.
    kwargs : dict
        Additional keyword arguments passed directly to websockets.connect
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.app.model.abstract.error import OpenBBError

    try:
        listener = Listener(**kwargs)
        listener.run(url, **kwargs)
    except Exception as e:  # pylint: disable=broad-except
        raise OpenBBError(e) from e
