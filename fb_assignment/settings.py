"""
Настройки web-приложения.
"""
from starlette.config import Config

config = Config('.env')

DEBUG = config('DEBUG', cast=bool, default=False)
DATABASE_URI = config('DATABASE_URI', cast=str,
                      default='redis://localhost:6379')
