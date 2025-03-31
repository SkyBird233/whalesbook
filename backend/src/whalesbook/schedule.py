from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from .config import Book
from .services.registry import Registry
from .state import update_book


scheduler = AsyncIOScheduler()


def schedule_books(cron: str, registry: Registry, books: list[Book], force=False):
    for book in books:
        scheduler.add_job(
            update_book,
            CronTrigger.from_crontab(cron),
            (registry, book, force),
        )
    scheduler.start()
