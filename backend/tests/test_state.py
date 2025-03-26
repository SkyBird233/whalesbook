from app.state import get_new_refs, stop_containers
from app.state import update_images, update_containers, delete_old_images, MainTag
from app.docker import get_containers
from pydantic import ValidationError
import logging
import pytest

pytestmark = pytest.mark.anyio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_main_tag():
    t_str = [
        "http://registry.example.com:5000/library/name:main",
        "localhost:5000/user/name:tag_vX.X.X",
        "https://registry.example.com/library/name:git-xxxxx",
        "library/name:some-tag_vX.X.X",
        "library/name",
        "https://registry:5000/library/name",
    ]
    for string in t_str:
        logger.info(MainTag.model_validate(string).to_string())

    f_str = ["name"]
    for string in f_str:
        with pytest.raises(ValidationError):
            logger.info(MainTag.model_validate(string).to_string())


async def test_update(settings, registry):
    book = settings.books[0]

    assert settings.docker_registry is not None

    ref_pairs_to_update, outdated_registry_hashes = await get_new_refs(registry, book)
    logger.debug(ref_pairs_to_update)
    logger.debug(outdated_registry_hashes)

    await update_images(registry.url, book, ref_pairs_to_update, dry_run=False)

    await update_containers(registry, book)

    containers = await get_containers(["whalesbook.main_tag"], book.runner)
    logger.info(containers)
    assert not containers[2]

    await stop_containers(registry.url, book)

    containers = await get_containers(["whalesbook.main_tag"], book.runner)
    logger.info(containers)
    assert not containers[0]

    await delete_old_images(registry, book)
