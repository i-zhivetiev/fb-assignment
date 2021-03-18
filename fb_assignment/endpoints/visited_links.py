"""
Модуль, обслуживающий эндпоинт посещённых ссылок.
"""
from datetime import datetime
from typing import List

from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from fb_assignment.endpoints.validators import validate_body
from fb_assignment.interfaces import storage
from fb_assignment.models import VisitedLinks


class VisitedLinksEndpoint(HTTPEndpoint):
    storage = storage

    @validate_body
    async def post(self, visited_links: VisitedLinks) -> JSONResponse:
        """Сохранить в БД уникальные домены из списка ссылок ``visited_links``
        и время их посещения. Временем посещения считается время на момент
        обработки запроса.

        :param visited_links:
            Список посещённых ссылок.
        """
        await self.storage.save_visited_domains(
            domains=self.get_unique_human_readable_hosts(visited_links),
            visit_timestamp=self.get_visit_timestamp(),
        )
        return JSONResponse({'status': 'ok'})

    @staticmethod
    def get_visit_timestamp() -> int:
        return round(datetime.utcnow().timestamp())

    @staticmethod
    def get_unique_human_readable_hosts(
            visited_links: VisitedLinks,
    ) -> List[str]:
        return list(
            set(i.human_readable_host for i in visited_links.links)
        )
