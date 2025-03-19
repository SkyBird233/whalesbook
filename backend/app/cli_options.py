from pathlib import Path
from app import config


class Options:
    def __init__(self, config_file: Path = Path("config.yml")):
        config_file = Path(config_file)
        if not config_file.exists():
            raise Exception(f"Config file not found: {config_file.absolute()}")

        self.config_file = config_file
        config.settings = config.Settings.from_yaml(Path(config_file))

    class config:
        def validate(self):
            print(f"Path: {config.settings.config_dir.resolve()}")
            print(config.settings.model_dump_json(indent=2))

    class book:
        def list(self):
            print("\n".join(book.name for book in config.settings.books))