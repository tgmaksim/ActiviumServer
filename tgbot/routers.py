from aiogram import Router


__all__ = ['get_tg_router']


def get_tg_router() -> Router:
    """Основной роутер для обработки событий Telegram-бота (сообщения, нажатия кнопок и др.)"""

    from .handlers import start, reviews, app, help, admin, school, menu, school_admins, school_posts, school_statistics, school_bells

    router = Router()
    router.include_router(reviews.router)
    router.include_router(app.router)
    router.include_router(help.router)
    router.include_router(admin.router)
    router.include_router(school.router)
    router.include_router(menu.router)
    router.include_router(school_admins.router)
    router.include_router(school_posts.router)
    router.include_router(school_statistics.router)
    router.include_router(school_bells.router)

    router.include_router(start.router)  # start всегда в конце, чтобы маршрутизировать deep link

    return router
