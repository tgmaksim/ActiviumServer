from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from .project_config import settings


__all__ = ['setup_openapi']

TITLE = "API учебного приложения «Активиум»"

SUMMARY = "Полная документация серверной части учебного приложения «Активиум»"

DESCRIPTION = (
    "Все запросы делятся на группы, а также разделяются на авторизованные и неавторизованные с необходимостью иметь "
    "активную сессию и нет соответственно. Независимо от типа запроса для всех требуется apiKey. В ответе всегда "
    "возвращается JSON, даже если возникнет критическая ошибка (кроме случаев выключенного сервера или "
    "нахождение в процессе перезапуска)\n"
    "Ключевой концепцией API является использование стабильных идентификаторов сущностей (classId). "
    "Каждый ответ опирается на classId, что позволяет клиентским приложениям разных версий "
    "корректно работать с API даже в случае изменения структуры данных или устаревания отдельных методов."
    "При изменении какого-ибо метода создается его новая версия, а старая продолжает работать\n"
    "Полный список идентификаторов сущностей доступен в соответствующих разделах документации\n\n"
    
    "Для авторизации необходимо отправить запрос login из группы Login. В ответе вернется сгенерированный "
    "идентификатор сессии и ссылка для ее авторизации. После перехода по ссылке и подтверждения прав от Дневника.ру "
    "ссылка становится авторизованной и по ней можно совершать запросы. После истечения времени действия сессии "
    "на любой авторизованный запрос вернется ошибка SessionError. При повторной авторизации можно передать "
    "идентификатор старой сессии, чтобы сервер повторно авторизовал ее"
)


def setup_openapi(app: FastAPI, hide_validation_errors: bool):
    """Настройка страницы openapi"""

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

        if hide_validation_errors:  # Скрытие лишних разделов документации
            for _, method_item in schema.get('paths').items():
                for _, param in method_item.items():
                    responses: dict = param.get('responses')
                    if '422' in responses:
                        # Удаление информации об ошибке RequestValidationError в документации, потому что
                        # данная ошибка перехватывается и генерируется своя
                        responses.pop('422')

            schemas: dict = schema.get('components', {}).get('schemas', {})

            if 'HTTPValidationError' in schemas:
                schemas.pop('HTTPValidationError')  # Удаление информации об ошибке HTTPValidationError в документации
            if 'ValidationError' in schemas:
                schemas.pop('ValidationError')  # Удаление информации об ошибке ValidationError в документации

        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
