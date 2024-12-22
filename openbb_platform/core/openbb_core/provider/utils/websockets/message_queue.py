"""Async WebSocket Message Queue."""

import logging
from typing import Optional


class MessageQueue:
    """Async message queue for the WebSocket connection."""

    def __init__(
        self,
        max_size: int = 10000,
        max_retries=5,
        backoff_factor=0.75,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize the MessageQueue."""
        # pylint: disable=import-outside-toplevel
        from asyncio import Queue  # noqa
        from openbb_core.provider.utils.websockets.helpers import get_logger

        self.queue: Queue = Queue(maxsize=max_size)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.logger = (
            logger
            if logger
            else get_logger("openbb.websocket.queue", level=logging.WARN)
        )

    async def dequeue(self):
        """Dequeue a message."""
        return await self.queue.get()

    async def enqueue(self, message):
        """Enqueue a message."""
        # pylint: disable=import-outside-toplevel
        from asyncio import sleep

        retries = 0
        while retries < self.max_retries:

            if self.queue.qsize() / self.queue.maxsize > 0.3:
                await sleep(0.00005)
            if self.queue.qsize() / self.queue.maxsize > 0.5:
                await sleep(0.00005)
            if self.queue.qsize() / self.queue.maxsize > 0.55:
                await sleep(0.00005)
            if self.queue.qsize() / self.queue.maxsize > 0.6:
                await sleep(0.00005)
            if self.queue.qsize() / self.queue.maxsize > 0.65:
                await sleep(0.00005)
            if self.queue.qsize() / self.queue.maxsize > 0.7:
                await sleep(0.00005)
            if self.queue.qsize() / self.queue.maxsize > 0.75:
                await sleep(0.00005)
            if self.queue.qsize() / self.queue.maxsize > 0.8:
                await sleep(0.00005)
            if self.queue.qsize() / self.queue.maxsize > 0.98:
                await sleep(0.0005)

            if self.queue.full():
                retries += 1
                msg = f"Queue is full. Retrying {retries}/{self.max_retries}..."
                self.logger.warning(msg)
                await sleep(self.backoff_factor * retries)
            else:
                await self.queue.put(message)
                return

        self.logger.warn("Failed to enqueue message after maximum retries.")

    async def process_queue(self, handler):
        """Process the message queue."""
        while True:
            message = await self.queue.get()
            await self._process_message(message, handler)
            self.queue.task_done()

    async def _process_message(self, message, handler):
        """Process the message with the handler coroutine."""
        await handler(message)
