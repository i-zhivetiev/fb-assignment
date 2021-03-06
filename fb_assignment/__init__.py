"""
funbox assignment
#################

Web-приложение для учета посещенных ссылок.

API
===

Тело запроса (где есть) и тело ответа -- JSON.

Точки входа
-----------

- ``POST /visited_links``
- ``GET /visited_domains``

POST /visited_links
~~~~~~~~~~~~~~~~~~~

Сохранить список переданных ссылок. Временем посещения ссылок считается время
выполнения запроса в UTC.

Тело запроса:

::

    {
        "links": [
            <str>, строка с URL,
            ...
        ]
    }

Тело ответа:

::

    {
        "status": <ok|error: bad request>
    }

Ошибки:

- 400 -- неверное тело запроса.


GET /visited_domains
~~~~~~~~~~~~~~~~~~~~

Вернуть список доменов, которые были посещены в заданный период.

Параметры запроса:

- ``from`` -- <int, начало интервала, секунды>;
- ``to`` -- <int, конец интервала, секунды>.

Интервал задаётся секундах с начала эпохи в UTC.

Тело ответа:

::

    {
        "status": <ok|error: bad request>
    }

Ошибки:

- 400 -- неверные параметры запроса.

"""
from fb_assignment.application import app
