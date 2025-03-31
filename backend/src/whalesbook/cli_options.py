from pathlib import Path
from anyio import sleep, run
from . import config
from .services import registry
from . import state
from .schedule import schedule_books
import logging

logger = logging.getLogger(__name__)


class Options:
    def __init__(self, config_file: Path = Path("config.yml"), verbose: bool = False):
        self.config_file = Path(config_file)
        logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)

        if not self.config_file.exists():
            logger.warning(f"Config file not found: {config_file.absolute()}")
            return

        config.settings = config.Settings.from_yaml(Path(config_file))

    async def test_log(self):
        logger.info("info")
        logger.debug("debug")

    class config:
        def validate(self):
            print(f"Path: {config.settings.config_dir.resolve()}")
            print(config.settings.model_dump_json(indent=2))

    class book:
        def __init__(self, all: bool = False, name: str = ""):
            if not name:
                logger.info("No book name specified, selecting all books")
                all = True
            self.books = (
                [book for book in config.settings.books if book.name == name]
                if not all
                else config.settings.books
            )

        def list(self):
            print("\n".join(book.name for book in self.books))

        async def update(self, force: bool = False):
            reg = await registry.create_registry(config.settings.docker_registry)  # type: ignore
            for book in self.books:
                await state.update_book(reg, book, force)

        async def stop_containers(self):
            reg = await registry.create_registry(config.settings.docker_registry)  # type: ignore
            for book in self.books:
                await state.stop_containers(reg.url, book)

        async def delete_old_images(self):
            reg = await registry.create_registry(config.settings.docker_registry)  # type: ignore
            for book in self.books:
                await state.delete_old_images(reg, book)

        def schedule_only(self, cron: str = config.settings.schedule.cron, force=False):
            async def main_loop():
                reg = await registry.create_registry(config.settings.docker_registry)  # type: ignore
                schedule_books(cron, reg, self.books)
                while True:
                    await sleep(100)

            try:
                run(main_loop)
            except (KeyboardInterrupt, SystemExit):
                pass
