from html import escape
from typing import Optional

from tgbot.notifier import send_admin_message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ...models.review_model import Review
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['ReviewRepository']


class ReviewRepository(SqlAlchemyRepository[Review]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Review)

    async def get_review(self, parent_id: int, only_is_open: bool = False) -> Optional[Review]:
        if only_is_open:
            return await self.get_single(Review.parent_id == parent_id, Review.is_open == True)
        return await self.get_single(Review.parent_id == parent_id)

    async def create_review(self, parent_id: int, name: str, stars: int, text: str, is_open: bool = False) -> Review:
        return await self.create({
            'parent_id': parent_id,
            'name': name,
            'stars': stars,
            'text': text,
            'is_open': is_open
        })

    async def open_review(self, parent_id: int) -> Optional[Review]:
        return await self.update({
            'is_open': True
        }, Review.parent_id == parent_id)

    async def update_review(self, parent_id: int, name: str, stars: int, text: str, is_updated: bool = True, is_open: bool = False) -> Review:
        return await self.update({
            'name': name,
            'stars': stars,
            'text': text,
            'is_updated': is_updated,
            'is_open': is_open
        }, Review.parent_id == parent_id)

    async def delete_review(self, parent_id: int):
        return await self.delete(Review.parent_id == parent_id)

    async def get_reviews_by_likes(self, offset: Optional[int], limit: int) -> list[Review]:
        return await self.get_multi(
            Review.is_open == True,
            orders_=(Review.likes.desc(), Review.created_at.desc()),
            offset=offset,
            limit=limit
        )

    async def get_reviews_by_max_stars(self, offset: Optional[int], limit: int) -> list[Review]:
        return await self.get_multi(
            Review.is_open == True,
            orders_=(Review.stars.desc(), Review.likes.desc(), Review.created_at.desc()),
            offset=offset,
            limit=limit
        )

    async def get_reviews_by_min_stars(self, offset: Optional[int], limit: int) -> list[Review]:
        return await self.get_multi(
            Review.is_open == True,
            orders_=(Review.stars, Review.likes.desc(), Review.created_at.desc()),
            offset=offset,
            limit=limit
        )

    async def like_review(self, parent_id: int) -> Optional[Review]:
        return await self.update({
            'likes': Review.likes + 1
        }, Review.parent_id == parent_id)

    async def delete_like(self, parent_id: int) -> Optional[Review]:
        return await self.update({
            'likes': Review.likes - 1
        }, Review.parent_id == parent_id)

    @staticmethod
    async def check_review(review: Review):
        await send_admin_message(
            f"Новый отзыв от {review.name}!\n"
            f"Оценка: {'<tg-emoji emoji-id="5435957248314579621">⭐️</tg-emoji>' * review.stars}\n"
            f"{f'<blockquote>{escape(review.text)}</blockquote>' if review.text else ''}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="Опубликовать", icon_custom_emoji_id="5206607081334906820", style='success',
                    callback_data=f"open_review|{review.parent_id}")],
                [InlineKeyboardButton(
                    text="Уведомить о нарушении", icon_custom_emoji_id="5420323339723881652", style='danger',
                    callback_data=f"block_review|{review.parent_id}")]
            ]))
