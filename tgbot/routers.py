from aiogram import Router


__all__ = ['get_tg_router']


def get_tg_router() -> Router:
    from .handlers import start, reviews, app, help, admin

    router = Router()
    router.include_router(start.router)
    router.include_router(reviews.router)
    router.include_router(app.router)
    router.include_router(help.router)
    router.include_router(admin.router)
    return router
