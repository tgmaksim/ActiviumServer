from fastapi.requests import Request
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from ..services.school_service import SchoolService
from ...dependencies.templates import get_templates
from ...dependencies.services import get_school_service


__all__ = ['router', 'public_router']

router = APIRouter(prefix='/school', tags=["School"])
public_router = APIRouter(prefix='/school', tags=["School"], include_in_schema=False)


@public_router.get(
    "/posts/{post_id}/",
    summary="Получение поста",
    description="Возвращает отрисованный пост со всеми параметрами и контентом",
    response_class=HTMLResponse
)
async def _post(
        request: Request,
        post_id: int,
        service: SchoolService = Depends(get_school_service)
) -> HTMLResponse:
    template_params = await service.get_post(post_id)

    templates = get_templates()
    response = templates.TemplateResponse(
        request=request,
        name=template_params.name,
        status_code=template_params.status_code,
        context=template_params.context
    )

    if template_params.cookies:
        for cookie in template_params.cookies:
            response.set_cookie(**cookie)

    return response