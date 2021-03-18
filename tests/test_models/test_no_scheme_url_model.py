from pydantic import BaseModel
from pytest import mark

from fb_assignment.models import NoSchemeUrl


class ModelToTest(BaseModel):
    url: NoSchemeUrl


@mark.parametrize('url,expected_url,expected_scheme', [
    ('example.test', 'example.test', ''),
    ('example.test/some-path', 'example.test/some-path', ''),
    ('http://example.test', 'http://example.test', 'http'),
    ('http://example.test/some-path', 'http://example.test/some-path', 'http'),
    ('https://example.test', 'https://example.test', 'https'),
    ('https://example.test/some-path', 'https://example.test/some-path',
     'https'),
])
def test_default_scheme(url, expected_url, expected_scheme):
    test_model = ModelToTest(url=url)
    assert str(test_model.url) == expected_url
    assert test_model.url.scheme == expected_scheme


@mark.parametrize('url,expected', [
    ('http://example.test', 'example.test'),
    ('http://почта.рф', 'почта.рф'),
    ('http://127.0.0.1', '127.0.0.1'),
    ('http://[::1]:80', '[::1]'),
])
def test_human_readable_host(url, expected):
    test_model = ModelToTest(url=url)
    assert test_model.url.human_readable_host == expected
