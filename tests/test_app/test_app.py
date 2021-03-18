from pytest import fixture


@fixture(autouse=True)
async def redis_flush_all(redis_client):
    await redis_client.execute('FLUSHALL')
    yield
    await redis_client.execute('FLUSHALL')


@fixture
def start():
    return 0


@fixture
def end(visit_timestamp):
    day = 60 * 60 * 24
    return visit_timestamp + day


@fixture
def client(app_client):
    # убедимся, что startup and shutdown вызываются
    with app_client:
        yield app_client


@fixture
def visited_domains_endpoint(start, end):
    return f'/visited_domains?from={start}&to={end}'


@fixture
def visited_links_endpoint():
    return '/visited_links'


def test_set_get(client, visited_domains_endpoint, visited_links_endpoint):
    response = client.get(visited_domains_endpoint)
    assert response.status_code == 200
    assert response.json() == {'domains': [],
                               'status': 'ok'}, 'database is not empty'

    body = {
        "links": [
            "https://ya.ru",
            "https://ya.ru?q=123",
            "funbox.ru",
            ("https://stackoverflow.com/questions/11828270"
             "/how-to-exit-the-vim-editor")
        ]
    }
    expected_domains = sorted(['ya.ru', 'funbox.ru', 'stackoverflow.com'])

    response = client.post(visited_links_endpoint, json=body)
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

    response = client.get(visited_domains_endpoint)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data['status'] == 'ok'
    assert sorted(response_data['domains']) == expected_domains
