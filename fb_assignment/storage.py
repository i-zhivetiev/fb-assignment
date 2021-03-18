"""
Интерфейс к БД, в которой хранятся ссылки.
"""
from typing import List

import aioredis
from aioredis import MultiExecError, WatchVariableError


class Storage:
    """Класс для работы с хранилищем ссылок. В качестве БД используется Redis.
    В качестве "низкоуровневого" интерфейса для доступа к Redis используется
    модуль aioredis [https://aioredis.readthedocs.io].

    В БД сохраняются только доменные имена, поэтому предполагается, что все
    данные, полученные из БД, являются валидными строками UTF-8.
    """

    def __init__(self, address, **kwargs):
        """Создать экземпляр Storage. Параметры совпадают с
        ``aioredis.create_redis_pool``. Дополнительно см.
        [https://aioredis.readthedocs.io/en/v1.3.1/api_reference.html].

        :param address:
            Адрес для подключения к Reids, может быть ``tuple`` в виде
            ``(host, port)`` или ``str``, которая содержит URI Redis или путь
            до сокета UNIX.
        :param kwargs:
            Дополнительные параметры, которые будут переданы в
            ``aioredis.create_redis_pool``.
        """
        self._address = address
        self._connection_options = kwargs
        self._encoding = 'utf-8'

        if 'encoding' not in kwargs:
            self._connection_options['encoding'] = self._encoding

        self._pool = None

    async def connect(self):
        if self.connected:
            return
        self._pool = await aioredis.create_redis_pool(
            self._address,
            **self._connection_options,
        )

    async def disconnect(self):
        if not self.connected:
            return
        self._pool.close()
        await self._pool.wait_closed()

    @property
    def connected(self):
        if self._pool is None:
            return False
        return not self._pool.closed

    @staticmethod
    def domains_key(visit_timestamp: int) -> str:
        """Вернуть имя ключа, в котором хранятся доменные имена, посещённые в
        момент ``visit_timestamp``.

        :param visit_timestamp:
            Время посещения, timestamp.
        """
        return f'domains-visited-at:{visit_timestamp}'

    @property
    def timestamps_key(self) -> str:
        """Ключ-индекс для поиска доменов в промежутке времени. Представляет
        собой отсортированное множество (sorted set), где

          - score -- время посещения доменов;
          - value -- имя ключа, где хранятся домены, посещённые во время score.
        """
        return 'timestamps'

    async def save_visited_domains(
            self,
            domains: List[str],
            visit_timestamp: int
    ) -> None:
        """Сохранить доменные имена из списка ``domains`` в БД.

        :param domains:
            Список доменных имён, которые нужно сохранить.
        :param visit_timestamp:
            Время доступа, timestamp.
        """
        if not domains:
            return
        domains_key = self.domains_key(visit_timestamp)
        transaction = self._pool.multi_exec()
        transaction.sadd(domains_key, *domains)
        transaction.zadd(self.timestamps_key, visit_timestamp, domains_key)
        await transaction.execute()

    async def get_visited_domains(self, start: int, end: int) -> List[str]:
        """Вернуть доменные имена, время посещения которых попадет в промежуток
        между ``start`` и ``end`` включительно.

        :param start:
            Начало интервала, метка времени.
        :param end:
            Конец интервала, метка времени.
        :return:
            Список найденных доменных имён.
        """
        while True:
            try:
                domains = await self._try_get_visited_domains(start, end)
            except WatchVariableError:
                continue
            return domains

    async def _try_get_visited_domains(
            self,
            start: int,
            end: int,
    ) -> List[str]:
        """Возбуждает ошибку :class:`aioredis.WatchVariableError`, если во
        время выполнения транзакции произошло изменение БД.
        """
        await self._pool.watch(self.timestamps_key)
        visit_time_keys = await self._get_visit_time_keys(start, end)
        if not visit_time_keys:
            await self._pool.unwatch()
            return []
        return await self._get_unique_domains(visit_time_keys)

    async def _get_visit_time_keys(self, start: int, end: int) -> List[str]:
        return await self._pool.zrangebyscore(
            self.timestamps_key,
            min=start,
            max=end,
        )

    async def _get_unique_domains(self, visit_time_keys):
        transaction = self._pool.multi_exec()
        future = transaction.sunion(*visit_time_keys)
        try:
            domains, = await transaction.execute()
        except MultiExecError:
            if not future.done():
                raise
            if isinstance(future.exception(), WatchVariableError):
                future.result()
            raise
        return domains
