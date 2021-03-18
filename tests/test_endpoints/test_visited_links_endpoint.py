import json
from unittest.mock import call

from pytest import mark, fixture

from fb_assignment.endpoints import VisitedLinksEndpoint
from fb_assignment.models import VisitedLinks


@fixture
def endpoint():
    return '/visited_links'


@fixture
def error_response():
    return {
        'status': 'error: bad request',
    }


@mark.parametrize('link,expected_domain', [
    ('http://ya.ru', 'ya.ru'),
    ('http://почта.рф', 'почта.рф'),
])
def test_save_visited_domains(
        link, expected_domain,
        app_client, endpoint, monkeypatch, mock_storage,
):
    body = {'links': [link]}

    visit_timestamp = 1
    monkeypatch.setattr(VisitedLinksEndpoint, 'storage', mock_storage)
    monkeypatch.setattr(VisitedLinksEndpoint, 'get_visit_timestamp',
                        lambda s: visit_timestamp)

    response = app_client.post(endpoint, json=body)

    assert response.status_code == 200, response.json()
    assert response.json() == {'status': 'ok'}

    assert mock_storage.save_visited_domains.called is True
    assert mock_storage.save_visited_domains.await_count == 1
    assert mock_storage.save_visited_domains.await_args == call(
        domains=[expected_domain],
        visit_timestamp=visit_timestamp,
    )


@mark.parametrize('body', [
    '', 'some-body', '[]', '{}', json.dumps({'links': 'hello'}),
])
def test_malformed_body(body, app_client, endpoint, error_response):
    response = app_client.post(endpoint, data=bytes(body, encoding='ascii'))
    assert response.status_code == 400
    assert response.json() == error_response


@mark.parametrize('links,expected', [
    (['http://example.test', 'example.test/', 'http://example.test/hello'],
     ['example.test']),
    (['http://почта.рф', 'почта.рф/', 'http://почта.рф/hello'],
     ['почта.рф']),
    (['http://microsoft.com', 'http://apple.com/iphone/', 'ya.ru',
      'http://127.0.0.1/get'],
     ['microsoft.com', 'apple.com', 'ya.ru', '127.0.0.1']),
])
def test_get_unique_hosts(links, expected):
    visited_links = VisitedLinks(links=links)
    result = VisitedLinksEndpoint.get_unique_human_readable_hosts(
        visited_links)
    assert sorted(result) == sorted(expected)
