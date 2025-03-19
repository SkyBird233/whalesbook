from app.config import settings
from pathlib import Path

print(settings.from_yaml(Path("../config/config.yml")).model_dump_json(indent=2))
