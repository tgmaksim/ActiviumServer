from aiogram import Router


__all__ = ['get_tg_router']


def get_tg_router() -> Router:
    """Основной роутер для обработки событий Telegram-бота (сообщения, нажатия кнопок и др.)"""

    from .handlers import start, reviews, app, help, admin, school, menu

    router = Router()
    router.include_router(start.router)
    router.include_router(reviews.router)
    router.include_router(app.router)
    router.include_router(help.router)
    router.include_router(admin.router)
    router.include_router(school.router)
    router.include_router(menu.router)

    return router
