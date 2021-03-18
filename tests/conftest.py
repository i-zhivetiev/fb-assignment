from datetime import datetime

import aioredis
from pytest import fixture
from starlette.config import environ
from starlette.testclient import TestClient

DATABASE_URI = 'redis://localhost:16379'
environ['DATABASE_URI'] = DATABASE_URI

# XXX: Импортируем после установки переменных окружения, чтобы избежать
#  starlette.config.EnvironError
from fb_assignment import app as application


@fixture
def app():
    return application


@fixture
def app_client(app):
    return TestClient(app)


@fixture
def redis_uri():
    return DATABASE_URI


@fixture
async def redis_client(redis_uri):
    client = await aioredis.create_connection(
        redis_uri,
        encoding='utf-8',
    )
    yield client
    client.close()
    await client.wait_closed()


@fixture
def now():
    return datetime.utcnow()


@fixture
def visit_timestamp(now):
    return round(now.timestamp())
