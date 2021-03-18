"""
Модели данных, используемые в web-приложении.
"""
from typing import Dict, List

from pydantic import AnyUrl, BaseModel


class NoSchemeUrl(AnyUrl):
    """Тип URL. Отличия от базового класса:

    - допускает отсутствие схемы в URL;
    - объявляет свойство ``human_readable_host``.
    """

    @classmethod
    def validate_parts(cls, parts: Dict[str, str]) -> Dict[str, str]:
        if parts['scheme'] is None:
            parts['scheme'] = ''
        return super().validate_parts(parts)

    @property
    def human_readable_host(self):
        """Человеко-читаемое имя домена. Актуально для интернациональных
        доменных имён. Подробнее см.
        https://pydantic-docs.helpmanual.io/usage/types/#international-domains
        """
        if self.host_type == 'int_domain':
            return bytes(self.host, encoding='ascii').decode('idna')
        return self.host


class VisitedLinks(BaseModel):
    links: List[NoSchemeUrl]


class SearchingInterval(BaseModel):
    start: int
    end: int
