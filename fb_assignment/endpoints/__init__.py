"""
Модуль с классами-эндпоинтами web-приложения.
"""
from starlette.routing import Route

from .visited_domains import VisitedDomainsEndpoint
from .visited_links import VisitedLinksEndpoint

routes = [
    Route('/visited_domains', VisitedDomainsEndpoint),
    Route('/visited_links', VisitedLinksEndpoint),
]
