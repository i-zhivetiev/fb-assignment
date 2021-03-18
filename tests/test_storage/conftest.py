from pytest import fixture

from fb_assignment.storage import Storage


@fixture
def storage(redis_uri):
    return Storage(address=redis_uri)


@fixture
async def test_storage(storage, redis_client):
    await redis_client.execute('FLUSHALL')
    await storage.connect()
    try:
        yield storage
        await storage.disconnect()
    finally:
        await redis_client.execute('FLUSHALL')


@fixture
def domains_key(storage, visit_timestamp):
    return storage.domains_key(visit_timestamp)


@fixture()
def timestamps_key(storage):
    return storage.timestamps_key


@fixture
def domains():
    return sorted(
        ['www.ru', 'www.dot.com', 'example', 'пример.рф', '127.0.0.1']
    )
