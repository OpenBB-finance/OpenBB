"""Unit Tests For MessageQueue Class."""

import asyncio

import pytest
from openbb_core.provider.utils.websockets.message_queue import MessageQueue

MOCK_MESSAGES = [
    {"message": "test1"},
    {"message": "test2"},
    {"message": "test3"},
]


@pytest.fixture
def message_queue():
    """Return a MessageQueue instance."""
    return MessageQueue(max_size=2, max_retries=2, backoff_factor=0.1)


@pytest.mark.asyncio
async def test_enqueue_dequeue(message_queue):
    """Test the enqueue and dequeue methods."""
    await message_queue.enqueue(MOCK_MESSAGES[0])
    assert not message_queue.queue.empty()
    await message_queue.enqueue(MOCK_MESSAGES[1])
    assert message_queue.queue.qsize() == 2
    assert await message_queue.dequeue() == MOCK_MESSAGES[0]
    assert message_queue.queue.qsize() == 1
    assert await message_queue.dequeue() == MOCK_MESSAGES[1]
    assert message_queue.queue.empty()


@pytest.mark.asyncio
async def test_enqueue_full(message_queue):
    """Test the enqueue method when the queue is full."""
    await message_queue.enqueue(MOCK_MESSAGES[0])
    await message_queue.enqueue(MOCK_MESSAGES[1])

    assert message_queue.queue.full()

    with pytest.warns(Warning):
        await message_queue.enqueue(MOCK_MESSAGES[2])
        assert message_queue.queue.qsize() == 2

    assert await message_queue.dequeue() == MOCK_MESSAGES[0]
    assert message_queue.queue.qsize() == 1
    await message_queue.enqueue(MOCK_MESSAGES[2])
    assert await message_queue.dequeue() == MOCK_MESSAGES[1]
    assert await message_queue.dequeue() == MOCK_MESSAGES[2]
    assert message_queue.queue.empty()


@pytest.mark.asyncio
async def test_process_queue(message_queue):
    """Test the process_queue method."""

    NUM_MESSAGES = 0

    async def handler(message):
        """Test handler."""
        nonlocal NUM_MESSAGES
        NUM_MESSAGES += 1

    await message_queue.enqueue(MOCK_MESSAGES[0])
    await message_queue.enqueue(MOCK_MESSAGES[1])
    asyncio.create_task(message_queue.process_queue(handler))
    await asyncio.sleep(0.1)
    assert NUM_MESSAGES == 2
