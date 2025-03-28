import pytest
from whalesbook.services.cli_runner import CliInstance

pytestmark = pytest.mark.anyio


async def test_cli_runner():
    cli = CliInstance()
    cli.add_arg("echo")
    cli.add_arg("test1")
    cli.add_arg("test2", "test3")
    result = await cli.run()
    assert result == ("test1 test2 test3", "", 0)


async def test_registry(settings, registry):
    assert settings.docker_registry
    repositories: list = registry.repositories

    if len(repositories):
        assert len(await registry.get_tags(repositories[0])) > 0
