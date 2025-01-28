from .template_manager import templates
from .config import settings

from .db import get_collection

__all__ = ("templates", "settings", "get_collection")
