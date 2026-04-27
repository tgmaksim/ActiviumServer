from typing import Annotated

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Query, Depends, Request, Header

from ..services.school_service import SchoolService
from ...dependencies.templates import get_templates
from ...dependencies.services import get_school_service
from ..schemas.school_schemas import SchoolPostsApiResponse, SchoolPostsWithoutVisionApiResponse, \
    SeeSchoolPostApiResponse, ClickSchoolPostApiResponse, ViewSchoolPostApiResponse, LikeSchoolPostApiResponse, \
    UnlikeSchoolPostApiResponse


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


@router.get(
    "/getPosts/0",
    summary="Получение постов",
    description="Получение последних постов, отсортированных по дате публикации",
    response_model=SchoolPostsApiResponse
)
async def _getPosts0(
        request: Request,
        offset: Annotated[int, Query(description="Смещение постов", ge=0)],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SchoolService = Depends(get_school_service)
) -> SchoolPostsApiResponse:
    request.state.session_id = sessionId
    return await service.getPosts(sessionId, offset)


@router.get(
    "/checkNewPosts/0",
    summary="Получение количества неувиденных постов",
    description="Получение количества неувиденных постов, но только тех, "
                "которые были опубликованы не ранее, чем 14 дней назад",
    response_model=SchoolPostsWithoutVisionApiResponse
)
async def _checkNewPosts0(
        request: Request,
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SchoolService = Depends(get_school_service)
) -> SchoolPostsWithoutVisionApiResponse:
    request.state.session_id = sessionId
    return await service.checkNewPosts(sessionId)


@router.put(
    "/seePost/0",
    summary="Увидеть пост",
    description="Пометить пост увиденным. После этого метод /checkNewPosts не будет считать его",
    response_model=SeeSchoolPostApiResponse
)
async def _seePost0(
        request: Request,
        postId: Annotated[int, Query(description="Идентификатор поста")],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SchoolService = Depends(get_school_service)
) -> SeeSchoolPostApiResponse:
    request.state.session_id = sessionId
    return await service.seePost(sessionId, postId)


@router.put(
    "/clickPost/0",
    summary="Нажать на пост",
    description="Пометить пост нажатым",
    response_model=ClickSchoolPostApiResponse
)
async def _clickPost0(
        request: Request,
        postId: Annotated[int, Query(description="Идентификатор поста")],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SchoolService = Depends(get_school_service)
) -> ClickSchoolPostApiResponse:
    request.state.session_id = sessionId
    return await service.clickPost(sessionId, postId)


@router.put(
    "/viewPost/0",
    summary="Просмотреть пост",
    description="Пометить пост просмотренным",
    response_model=ViewSchoolPostApiResponse
)
async def _viewPost0(
        request: Request,
        postId: Annotated[int, Query(description="Идентификатор поста")],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SchoolService = Depends(get_school_service)
) -> ViewSchoolPostApiResponse:
    request.state.session_id = sessionId
    return await service.viewPost(sessionId, postId)


@router.put(
    "/likePost/0",
    summary="Поставить реакцию на пост",
    description="Поставить реакцию на пост",
    response_model=LikeSchoolPostApiResponse
)
async def _likePost0(
        request: Request,
        postId: Annotated[int, Query(description="Идентификатор поста")],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SchoolService = Depends(get_school_service)
) -> LikeSchoolPostApiResponse:
    request.state.session_id = sessionId
    return await service.likePost(sessionId, postId)


@router.put(
    "/unlikePost/0",
    summary="Убрать реакцию с поста",
    description="Убрать реакцию с поста",
    response_model=UnlikeSchoolPostApiResponse
)
async def _unlikePost0(
        request: Request,
        postId: Annotated[int, Query(description="Идентификатор поста")],
        sessionId: Annotated[str, Header(description="Идентификатор сессии", min_length=1, max_length=32)],
        service: SchoolService = Depends(get_school_service)
) -> UnlikeSchoolPostApiResponse:
    request.state.session_id = sessionId
    return await service.unlikePost(sessionId, postId)
