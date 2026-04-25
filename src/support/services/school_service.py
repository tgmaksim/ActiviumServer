from html import escape
from typing import Callable, Any, Optional

from httpx import AsyncClient
from fastapi import HTTPException

from ...dependencies.datetime import astimezone
from ...services.html_response import HtmlResponse

from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork


__all__ = ['SchoolService']


class SchoolService(BaseService[AppUnitOfWork]):
    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client

    async def get_post(self, post_id: int) -> HtmlResponse:
        async with self.uow_factory() as uow:
            post = await uow.school_post_repository.get_post(post_id)

            if post is None:
                raise HTTPException(404)

            content = [{
                'type': block['type'],
                'text': self._format_to_html(block['text'], block['entities'])
            } for block in post.content]

            return HtmlResponse(name='post.html', context={
                'title': post.title,
                'description': post.description,
                'has_image': post.has_image,
                'schedule_date': post.schedule_date and post.schedule_date.strftime('%e %b.').strip(),
                'is_updated': post.is_updated,
                'count_viewings': post.count_viewings,
                'count_likes': post.count_likes,
                'content': content,
                'created_at': astimezone(post.created_at, post.timezone).strftime('%e %b. в %H:%M').strip()
            })

    @classmethod
    def _add_surogate(cls, text: str) -> bytes:
        return text.encode("utf-16-le")

    @classmethod
    def _remove_surogate(cls, text: bytes) -> str:
        return text.decode("utf-16-le")

    @classmethod
    def _format_to_html(cls, text: Optional[str], entities: list[dict[str, Any]]) -> Optional[str]:
        if text is None:
            return None

        surogate_text = cls._add_surogate(text)

        tags = {
            'bold': ('<b>', '</b>'),
            'italic': ('<i>', '</i>'),
            'underline': ('<u>', '</u>'),
            'strikethrough': ('<s>', '</s>'),
            'blockquote': ('<blockquote>', '</blockquote>'),
            'expandable_blockquote': ('<blockquote expandable>', '</blockquote>'),
        }

        # (индекс, приоритет, тег)
        events: list[tuple[int, int, str]] = []

        for entity in entities:
            e_type = entity['type']
            start = entity['offset'] * 2
            end = start + entity['length'] * 2

            if e_type == 'url':
                link_text = cls._remove_surogate(surogate_text[start:end])
                open_tag = f"<a href='{escape(link_text)}'>"
                close_tag = "</a>"
            elif e_type == 'text_link':
                open_tag = f"<a href='{escape(entity['url'])}'>"
                close_tag = "</a>"
            elif e_type in tags:
                open_tag, close_tag = tags[e_type]
            else:
                continue

            events.append((start, 1, open_tag))
            events.append((end, 0, close_tag))

        events.sort(key=lambda x: (x[0], x[1]))

        result = []
        last_pos = 0

        for pos, _, tag in events:
            result.append(escape(cls._remove_surogate(surogate_text[last_pos:pos])))
            result.append(tag)
            last_pos = pos

        result.append(escape(cls._remove_surogate(surogate_text[last_pos:])))

        return ''.join(result)