"""
Валидаторы для тела и параметров HTTP-запроса.
"""
from functools import wraps
from json.decoder import JSONDecodeError
from typing import Callable

from pydantic import ValidationError
from starlette.responses import JSONResponse

from fb_assignment.models import VisitedLinks, SearchingInterval


def validate_body(method: Callable) -> Callable:
    """Декоратор для валидации тела запроса. Используется для оборачивания
    методов наследников :class:`starlette.endpoints.HTTPEndpoint`.

    Возвращает ошибку, если:
      - тело запроса не удалось разобрать;
      - возникла ошибка валидации при создании экземпляра модели данных.

    В случае успеха вызывает обёрнутый метод, передав в качестве параметра
    экземпляр модели.

    TODO: параметризовать моделью, в случае появления эндпоинтов кроме
     :class:`visited_links.VisitedLinksEndpoint`
    """
    error = JSONResponse(
        content={'status': 'error: bad request'},
        status_code=400,
    )

    @wraps(method)
    async def wrapper(self, request):
        try:
            body = await request.json()
        except (JSONDecodeError, TypeError):
            return error

        if not isinstance(body, dict):
            return error

        try:
            visited_links = VisitedLinks(**body)
        except ValidationError as _:
            return error

        return await method(self, visited_links)

    return wrapper


def validate_query(method: Callable) -> Callable:
    """Декоратор для валидации тела запроса. Используется для оборачивания
    методов наследников :class:`starlette.endpoints.HTTPEndpoint`.

    Возвращает ошибку, если:
      - параметры запроса не удалось разобрать;
      - возникла ошибка валидации при создании экземпляра модели данных.

    В случае успеха вызывает обёрнутый метод, передав в качестве параметра
    экземпляр модели.

    TODO: параметризовать моделью, в случае появления эндпоинтов кроме
     :class:`visited_links.VisitedDomainsEndpoint`
    """
    error = JSONResponse(
        content={'status': 'error: bad request'},
        status_code=400,
    )

    @wraps(method)
    async def wrapper(self, request):
        try:
            params = {
                'start': request.query_params['from'],
                'end': request.query_params['to'],
            }
        except KeyError:
            return error

        try:
            interval = SearchingInterval(**params)
        except ValidationError:
            return error

        return await method(self, interval)

    return wrapper
