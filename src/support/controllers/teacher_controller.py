from yarl import URL
from typing import Annotated, Optional

from fastapi.params import Cookie, Form
from starlette.responses import RedirectResponse
from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse, FileResponse

from ..services.teacher_service import TeacherService
from ...config.project_config import settings

from ...dependencies.templates import get_templates
from ...dependencies.services import get_teacher_service


__all__ = ['public_router']

public_router = APIRouter(prefix='/teacher', tags=["Teacher"])
"""Публичный router сайта"""


@public_router.get("", include_in_schema=False)
async def _root(
        request: Request,
        teacher_session_id: Annotated[Optional[str], Cookie(description="Идентификатор сессии учителя")] = None,
        service: TeacherService = Depends(get_teacher_service)
):
    template_params = await service.root(teacher_session_id)

    return template_params.to_response(request)


@public_router.get(
    "/auth",
    summary="Первичное и вторичное получение параметров от дневника.ру. Авторизация учителя",
    description="После авторизации дневник.ру перенаправит пользователя в данный метод, а здесь будет возвращен HTML. "
                "JS возьмет полученные параметры из url#hash и отправит в url?query. После вторичного получения "
                "параметров от дневника.ру они используются для авторизации",
    response_class=HTMLResponse, include_in_schema=False
)
async def _auth(
        request: Request,
        access_token: Annotated[Optional[str], Query(description="Токен для взаимодействия с дневником.ру от имени пользователя", min_length=1, max_length=64)] = None,
        service: TeacherService = Depends(get_teacher_service)
) -> HTMLResponse:
    if access_token is not None:
        template_params = await service.secondAuth(access_token)

        if template_params.status_code // 100 != 2:  #2xx
            templates = get_templates()
            response = templates.TemplateResponse(
                request=request,
                name=template_params.name,
                status_code=template_params.status_code,
                context=template_params.context
            )
        else:
            path = request.url.path
            path = '/'.join(path.strip('/').split('/')[:-1])  # Убрать auth

            response = RedirectResponse(
                url=str(URL(settings.URL).joinpath(path))
            )

        if template_params.cookies:
            for cookie in template_params.cookies:
                response.set_cookie(**cookie)

        if template_params.delete_cookies:
            for cookie in template_params.delete_cookies:
                response.delete_cookie(**cookie)

        return response

    else:
        template_params = await service.firstAuth()

        return template_params.to_response(request)


@public_router.post(
    "/report",
    summary="Создание отчета об успеваемости",
    description="Создание отчета для печати об успеваемости учеников класса (все оценки по предметам)",
    response_class=FileResponse, include_in_schema=True
)
async def _create_report(
        teacher_session_id: Annotated[str, Cookie(description="Идентификатор сессии учителя")],
        groupId: Annotated[int, Form(description="Идентификатор учебной группы (класса)")],
        service: TeacherService = Depends(get_teacher_service)
) -> FileResponse:
    file = await service.create_report(teacher_session_id, groupId)
    return FileResponse(
        file,
        filename="Отчет по классу.pdf",
        media_type='application/octet-stream'
    )
