from unittest.mock import create_autospec

from pytest import fixture

from fb_assignment.storage import Storage


@fixture
def mock_storage():
    return create_autospec(Storage)
