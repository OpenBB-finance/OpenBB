"""Convenience tool for listening to raw broadcast streams outside of the main application thread."""


class Listener:
    """WebSocket broadcast listener. Not intended to be initialized directly, use the 'listen' function."""

    def __init__(self, **kwargs):
        """Initialize the Listener. All keyword arguments are passed directly to websockets.connect."""

        self.loop = None
        self.websocket = None
        self.current_task = None
        self.kwargs = {}
        if kwargs:
            self.kwargs = kwargs

    async def listen(self, url, **kwargs):  # noqa: PLR0915
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
                        self.logger.info(
                            f"\nListening for messages from {clean_message(url)}"
                        )
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
                    self.logger.error(
                        f"The process hosting {clean_message(url)} was terminated."
                    )
                    break
                except websockets.exceptions.InvalidURI as error:
                    self.logger.error(f"Invalid URI -> {error}")
                    break
                except InvalidStatusCode as error:
                    self.logger.error(f"Invalid status code -> {error}")
                    break
                except OSError as error:
                    if "Multiple exceptions" in str(error):
                        err = str(error).split("Multiple exceptions:")[1].strip()
                        err = err.split("[")[-1].strip().replace("]", ":")
                        self.logger.error(
                            f"An error occurred while attempting to connect to: {clean_message(url)} -> {err}"
                        )
                    else:
                        self.logger.error(
                            f"An error occurred while attempting to connect to: {clean_message(url)} -> {error}"
                        )
                    break
        except Exception as error:
            self.logger.error(f"An unexpected error occurred: {error}")
            raise OpenBBError(error) from error
        finally:
            if self.websocket:
                await self.websocket.close()

    def stop(self):
        if self.current_task:
            self.current_task.cancel()
            self.loop.run_until_complete(self.current_task)
        if self.websocket:
            self.loop.run_until_complete(self.websocket.close())
        if not self.loop.is_closed():
            self.loop.stop()

    async def start_listening(self, url, **kwargs):
        # pylint: disable=import-outside-toplevel
        import asyncio
        import contextlib

        self.current_task = self.loop.create_task(self.listen(url, **kwargs))
        with contextlib.suppress(asyncio.CancelledError):
            await self.current_task

    def run(self, url, **kwargs):
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
            self.logger.info("\nWebSocket listener terminated.")
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
    except Exception as e:
        raise OpenBBError(e) from e
    finally:
        return
