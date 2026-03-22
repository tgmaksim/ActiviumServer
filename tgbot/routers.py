from aiogram import Router


__all__ = ['get_tg_router']


def get_tg_router() -> Router:
    from .handlers import start, reviews

    router = Router()
    router.include_router(start.router)
    router.include_router(reviews.router)
    return router
