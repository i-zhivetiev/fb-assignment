import random

from pytest import mark, fixture

pytestmark = mark.asyncio


@fixture
def get_random_domains(domains):
    def _get_domains(d=domains):
        k = random.randrange(1, len(d))
        return random.choices(d, k=k)

    return _get_domains


@fixture
def get_expected_domains():
    def _get_expected_domains(domains):
        return sorted(list(set(domains)))

    return _get_expected_domains


async def test_get_domains(test_storage, domains, visit_timestamp):
    await test_storage.save_visited_domains(
        domains=domains,
        visit_timestamp=visit_timestamp,
    )
    result = await test_storage.get_visited_domains(
        start=visit_timestamp - 1,
        end=visit_timestamp + 1,
    )
    assert domains == sorted(result)


async def test_get_domains_within_interval(
        get_random_domains, get_expected_domains, test_storage,
        visit_timestamp,
):
    expected_domains = set()

    offsets_within_interval = 0, 1, 2, 3
    for offset in offsets_within_interval:
        domains = get_random_domains()
        await test_storage.save_visited_domains(
            domains=domains,
            visit_timestamp=visit_timestamp + offset,
        )
        expected_domains.update(get_expected_domains(domains))

    offsets_outside_interval = -10, -5, 5, 10
    for offset in offsets_outside_interval:
        domains = get_random_domains(['some', 'else', 'domains', 'here.com'])
        await test_storage.save_visited_domains(
            domains=domains,
            visit_timestamp=visit_timestamp + offset,
        )

    result = await test_storage.get_visited_domains(
        start=visit_timestamp - 1,
        end=visit_timestamp + offsets_within_interval[-1] + 1,
    )

    assert sorted(list(expected_domains)) == sorted(result)


async def test_get_domains_on_edges(
        test_storage, get_random_domains, get_expected_domains,
        visit_timestamp,
):
    offsets = -10, -5, 0, 5, 10
    expected_domains = dict()
    for offset in offsets:
        domains = get_random_domains()
        await test_storage.save_visited_domains(
            domains=domains,
            visit_timestamp=visit_timestamp + offset,
        )
        expected_domains[offset] = get_expected_domains(domains)

    result = await test_storage.get_visited_domains(
        start=0,
        end=visit_timestamp + offsets[0],
    )
    assert expected_domains[offsets[0]] == sorted(result)

    result = await test_storage.get_visited_domains(
        start=visit_timestamp + offsets[-1],
        end=visit_timestamp * 10,
    )
    assert expected_domains[offsets[-1]] == sorted(result)


async def test_get_domains_on_empty_storage(test_storage, redis_client):
    assert await redis_client.execute('KEYS', '*') == []
    result = await test_storage.get_visited_domains(start=0, end=1)
    assert result == []


@mark.parametrize('start,end', [
    (1, 0),
    (1, 1),
    (0, 0),
])
async def test_start_end(start, end, test_storage, redis_client):
    assert await redis_client.execute('KEYS', '*') == []
    result = await test_storage.get_visited_domains(start=start, end=end)
    assert result == []


async def test_get_no_domains_outside_interval(
        test_storage, get_random_domains, visit_timestamp,
):
    await test_storage.save_visited_domains(
        domains=get_random_domains(),
        visit_timestamp=visit_timestamp,
    )
    result = await test_storage.get_visited_domains(
        start=visit_timestamp - 2,
        end=visit_timestamp - 1,
    )
    assert result == []
