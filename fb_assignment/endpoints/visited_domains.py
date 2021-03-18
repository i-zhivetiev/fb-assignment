"""
Модуль, обслуживающий эндпонит посещённых доменов.
"""

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from fb_assignment.endpoints.validators import validate_query
from fb_assignment.interfaces import storage
from fb_assignment.models import SearchingInterval


class VisitedDomainsEndpoint(HTTPEndpoint):
    storage = storage

    @validate_query
    async def get(self, interval: SearchingInterval) -> JSONResponse:
        """Получить список уникальных доменов, посещённых в интервале
        ``interval``.

        :param interval:
            Интервал, в котором нужно искать домены.
        """
        domains = await self.storage.get_visited_domains(
            start=interval.start,
            end=interval.end,
        )
        return JSONResponse({
            'domains': domains,
            'status': 'ok',
        })
