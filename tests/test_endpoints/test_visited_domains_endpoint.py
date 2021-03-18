from unittest.mock import call

from pytest import mark

from fb_assignment.endpoints import VisitedDomainsEndpoint


def test_get_visited_domains(app_client, mock_storage, monkeypatch):
    domains = ['test.example']
    start = 0
    end = 1

    mock_storage.get_visited_domains.return_value = domains
    monkeypatch.setattr(VisitedDomainsEndpoint, 'storage', mock_storage)

    response = app_client.get(f'/visited_domains?from={start}&to={end}')

    assert response.status_code == 200, response.json()
    assert response.json() == {'domains': domains, 'status': 'ok'}

    assert mock_storage.get_visited_domains.called is True
    assert mock_storage.get_visited_domains.await_count == 1
    assert mock_storage.get_visited_domains.await_args == call(
        start=start, end=end,
    )


@mark.parametrize('endpoint', [
    '/visited_domains',
    '/visited_domains?',
    '/visited_domains?start=10&stop=15',
    '/visited_domains?from=1',
    '/visited_domains?to=2',
    '/visited_domains?from=hello&to=2',
    '/visited_domains?from=0&to=one',
])
def test_malformed_query(endpoint, app_client):
    response = app_client.get(endpoint)
    assert response.status_code == 400
    assert response.json() == {'status': 'error: bad request'}
