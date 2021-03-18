from fb_assignment.storage import Storage


def test_storage_init(redis_uri):
    storage = Storage(address=redis_uri)
    assert storage._address == redis_uri
    assert storage.connected is False
    assert storage._connection_options == {'encoding': 'utf-8'}
