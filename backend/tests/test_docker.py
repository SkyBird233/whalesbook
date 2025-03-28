import pytest
from whalesbook import docker
import logging

pytestmark = pytest.mark.anyio

logger = logging.getLogger(__name__)


async def test_get_containers():
    stdout, stderr, code = await docker.get_containers()
    logger.info(stdout)
    assert code == 0 and type(stdout) is list


async def test_container_run_and_stop():
    container_name = "test_nginx"
    image = "registry.skybirds.sbs/library/nginx:alpine"
    labels = ["test1=t1", "test2=t2"]

    stdout, stderr, code = await docker.run_container(
        image,
        None,
        container_name,
        None,
        labels,
        None,
    )
    logger.info(stdout)
    assert code == 0

    stdout, stderr, code = await docker.get_containers(labels=labels)
    logger.info(stdout)
    assert code == 0 and type(stdout) is list and len(stdout) == 1
    assert stdout[0]["Names"] == container_name

    stdout, stderr, code = await docker.stop_container(container_name)
    logger.info(stdout)
    assert code == 0

    stdout, stderr, code = await docker.get_containers(labels=[image])
    assert code == 0 and stdout == ""
