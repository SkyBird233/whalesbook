from app.state import get_new_refs, stop_containers
from app.state import update_images, update_containers
from app.docker import get_containers
import logging
import pytest

pytestmark = pytest.mark.anyio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_update(settings, registry):
    book = settings.books[0]

    assert settings.docker_registry is not None

    ref_pairs_to_update, outdated_registry_hashes = await get_new_refs(book, registry)
    logger.debug(ref_pairs_to_update)
    logger.debug(outdated_registry_hashes)

    await update_images(registry.url, book, ref_pairs_to_update, dry_run=False)

    await update_containers(registry, book)

    containers = await get_containers(["whalesbook.main_tag"], book.runner)
    logger.info(containers)
    assert not containers[2]

    await stop_containers(book)

    containers = await get_containers(["whalesbook.main_tag"], book.runner)
    logger.info(containers)
    assert not containers[0]
