from starlette.templating import Jinja2Templates

from ..config.project_config import settings

from functools import lru_cache


__all__ = ['get_templates']


@lru_cache()
def get_templates() -> Jinja2Templates:
    """Папка с html-файлами. Кешируется на время работы"""

    return Jinja2Templates(directory=settings.TEMPLATES_DIRECTORY)
