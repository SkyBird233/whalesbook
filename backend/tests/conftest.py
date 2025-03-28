import pytest
from pathlib import Path
from whalesbook.config import Settings
from whalesbook.services.registry import create_registry


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def settings():
    default_path = Path("config/config.yml")
    if not default_path.exists():
        default_path = Path("tests") / default_path
    return Settings.from_yaml(default_path)


@pytest.fixture
async def registry(settings):
    return await create_registry(settings.docker_registry)
