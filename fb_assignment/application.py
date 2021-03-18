"""
Модуль, отвечающий за создание web-приложения.
"""
from starlette.applications import Starlette

from fb_assignment import settings
from fb_assignment.endpoints import routes
from fb_assignment.interfaces import storage


async def on_startup():
    await storage.connect()


async def on_shutdown():
    await storage.disconnect()


app = Starlette(
    debug=settings.DEBUG,
    routes=routes,
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
)
