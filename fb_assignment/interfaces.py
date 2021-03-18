"""
Интерфейсы. Используются в классах, которые обслуживают эндпоинты.
"""
from fb_assignment import settings
from fb_assignment.storage import Storage

storage = Storage(settings.DATABASE_URI)
