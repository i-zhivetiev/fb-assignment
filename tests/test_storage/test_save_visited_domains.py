from pytest import mark, fixture

pytestmark = mark.asyncio


@fixture
def get_domains(redis_client, domains_key):
    async def _get_domains(key=domains_key):
        result = await redis_client.execute('SMEMBERS', key)
        return sorted(result)

    return _get_domains


@fixture
def get_bins(redis_client, timestamps_key):
    async def _get_bins(bins=timestamps_key):
        result = await redis_client.execute(
            'ZRANGE', bins, 0, -1, 'WITHSCORES',
        )
        return result

    return _get_bins


@mark.parametrize('domain', [
    'ya.ru', '127.0.0.1', 'example', 'почта.рф',
])
async def test_save_domain(
        domain,
        test_storage, visit_timestamp, domains_key, get_domains, get_bins,
):
    domains = [domain]
    await test_storage.save_visited_domains(
        domains=domains,
        visit_timestamp=visit_timestamp,
    )
    assert domains == await get_domains()
    assert [domains_key, str(visit_timestamp)] == await get_bins()


async def test_save_domains(
        test_storage, visit_timestamp, domains_key, domains, get_domains,
        get_bins,
):
    await test_storage.save_visited_domains(
        domains=domains,
        visit_timestamp=visit_timestamp,
    )
    assert domains == await get_domains()
    assert [domains_key, str(visit_timestamp)] == await get_bins()


async def test_several_calls(
        test_storage, domains, get_domains, get_bins, visit_timestamp,
        domains_key
):
    await test_storage.save_visited_domains(
        domains=domains,
        visit_timestamp=visit_timestamp,
    )
    extra_domains = ['extra.domain']
    extra_visit_time = visit_timestamp + 1
    extra_bin = test_storage.domains_key(extra_visit_time)
    await test_storage.save_visited_domains(
        domains=extra_domains,
        visit_timestamp=extra_visit_time,
    )
    assert domains == await get_domains()
    assert extra_domains == await get_domains(extra_bin)
    assert [domains_key, str(visit_timestamp),
            extra_bin, str(extra_visit_time)] == await get_bins()


async def test_empty_list(test_storage, visit_timestamp, get_domains,
                          get_bins):
    await test_storage.save_visited_domains(
        domains=[],
        visit_timestamp=visit_timestamp,
    )
    assert [] == await get_domains()
    assert [] == await get_bins()


async def test_save_to_existing_bin(
        test_storage, domains, get_domains, get_bins, visit_timestamp,
        domains_key,
):
    await test_storage.save_visited_domains(
        domains=domains,
        visit_timestamp=visit_timestamp,
    )
    extra_domain = 'extra.domain'
    assert extra_domain not in domains
    domains_plus = domains + [extra_domain, domains[0]]
    await test_storage.save_visited_domains(
        domains=domains_plus,
        visit_timestamp=visit_timestamp,
    )
    expected_domains = sorted(list(set(domains_plus)))
    assert expected_domains == await get_domains()
    assert [domains_key, str(visit_timestamp)] == await get_bins()
