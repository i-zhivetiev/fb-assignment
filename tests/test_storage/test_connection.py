import pytest
from pytest import raises

from fb_assignment.storage import Storage

pytestmark = pytest.mark.asyncio


async def test_connect_disconnect(storage):
    assert storage.connected is False
    await storage.connect()
    assert storage.connected is True
    await storage.disconnect()
    assert storage.connected is False


async def test_double_connect(storage):
    assert storage.connected is False
    await storage.connect()
    assert storage.connected is True
    await storage.connect()
    await storage.disconnect()


async def test_disconnect_on_no_pool(storage):
    assert storage.connected is False
    await storage.disconnect()


async def test_no_connection(unused_tcp_port):
    storage = Storage(('localhost', unused_tcp_port))
    with raises(OSError):
        await storage.connect()
