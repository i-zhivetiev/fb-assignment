## Что это?

Web-приложение для учёта посещённых доменов. Описание API см. в докстринге
модуля `fb_assignment`.

## Как запустить?

### Требования

- Redis ≥ 6.0
- Python 3.8
- [Pipenv](https://pipenv.pypa.io/en/latest/)

### Установка

Получить клон репозитория с приложением:

```bash
$ git clone https://github.com/i-zhivetiev/fb-assignment.git
```

Создать виртуальное окружение и установить зависимости:

```bash
$ cd fb-assignment
$ pipenv sync --dev
```

### Запуск

Убедится, что Redis доступен по адресу `localhost:6379`. Например,

```bash
$ redis-cli ping
PONG
```

Запустить приложение:

```bash
$ pipenv run uvicorn fb_assignment:app
INFO:     Started server process [15771]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

После запуска сервер будет доступен по адресу `http://127.0.0.1:8000`.

### Конфигурация

Приложение настраивается с помощью переменных окружения:

- `DATABASE_URI` — URI Redis; по умолчанию — `redis://localhost:6379`.

## Как протестировать?

### Вручную

Может быть удобно узнать текущую метку времени:

```bash
$ python -c 'import datetime; print(round(datetime.datetime.utcnow().timestamp()))'
```

Выполнить HTTP-запросы. Например, с помощью [HTTPie](https://httpie.io):

```bash
$ http ':8000/visited_domains?from=0&to=1700000000'
HTTP/1.1 200 OK
content-length: 28
content-type: application/json
date: Wed, 31 Mar 2021 09:38:58 GMT
server: uvicorn

{
    "domains": [],
    "status": "ok"
}
```

```bash
$ echo '{ "links": [ "http://example.test/path;parameters?query#fragment" ] }' \
  | http POST ':8000/visited_links'
HTTP/1.1 200 OK
content-length: 15
content-type: application/json
date: Wed, 31 Mar 2021 09:42:20 GMT
server: uvicorn

{
    "status": "ok"
}
```

```bash
$ http ':8000/visited_domains?from=0&to=1700000000'
HTTP/1.1 200 OK
content-length: 42
content-type: application/json
date: Wed, 31 Mar 2021 09:43:34 GMT
server: uvicorn

{
    "domains": [
        "example.test"
    ],
    "status": "ok"
}
```

### pytest

Для тестов стоит использовать отдельный экземпляр Redis -- база очищается после
каждой тестовой сессии. По умолчанию Redis для тестов должен быть доступен по
адресу `localhost:16379`. Другой адрес можно задать с помощью
переменной `tests.conftest.DATABASE_URI`.

Чтобы запустить тесты, нужно перейти в директорию с приложением и запустить
pytest:

```bash
$ cd fb-assignment
$ pipenv run python -m pytest
```
