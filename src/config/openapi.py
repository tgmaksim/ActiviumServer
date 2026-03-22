from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from .project_config import settings


__all__ = ['setup_openapi']

TITLE = "API школьного приложения «Активиум»"

SUMMARY = "Полная документация API серверной части школьного приложения «Активиум»"

DESCRIPTION = (
    "Документация описывает публичный API серверной части приложения «Активиум».\n\n"
    "Ключевой концепцией API является использование стабильных идентификаторов сущностей (classId). "
    "Каждый запрос и ответ опирается на classId, что позволяет клиентским приложениям разных версий "
    "корректно работать с API даже в случае изменения структуры данных или устаревания отдельных методов.\n\n"
    "Полный список идентификаторов сущностей доступен в соответствующих разделах документации."
)


def setup_openapi(app: FastAPI, hide_validation_errors: bool):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=TITLE,
            summary=SUMMARY,
            description=DESCRIPTION,
            contact={
                "name": settings.AUTHOR,
                "url": settings.AUTHOR_LINK
            },
            version=settings.VERSION,
            routes=app.routes,
        )

        if hide_validation_errors:
            for _, method_item in schema.get('paths').items():
                for _, param in method_item.items():
                    responses: dict = param.get('responses')
                    if '422' in responses:
                        responses.pop('422')  # Удаление информации об ошибке RequestValidationError в документации

            schemas: dict = schema.get('components', {}).get('schemas', {})

            if 'HTTPValidationError' in schemas:
                schemas.pop('HTTPValidationError')  # Удаление информации об ошибке HTTPValidationError в документации
            if 'ValidationError' in schemas:
                schemas.pop('ValidationError')  # Удаление информации об ошибке ValidationError в документации

        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
