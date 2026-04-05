import sys
import locale
import asyncio


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise ValueError("cron not found")

    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # Для работы datetime

    cron = sys.argv[1]
    if cron == "statistics":
        from crons import statistics
        asyncio.run(statistics.main())
    elif cron == "clear":
        from crons import clear
        asyncio.run(clear.main())
    else:
        raise ValueError("cron not found")
