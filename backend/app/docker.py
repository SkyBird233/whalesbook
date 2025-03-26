from pydantic import AnyUrl
from pathlib import Path
from app.services.cli_runner import CliInstance
from app.config import settings, TraefikConfig
import logging
from json import loads

logger = logging.getLogger(__name__)


async def build_image(
    tags: list[str],
    build_context: AnyUrl | Path | str,
    docker_context: str = "default",
    docker_file: Path | None = None,
    push: bool = False,
    dry_run: bool = False,
):
    default_labels = [
        f"whalesbook.main_tag={tags[0]}",
        f"whalesbook.git_tag={tags[1]}",
        f"whalesbook.build_context={build_context}",
    ]

    cli = CliInstance()

    cli.add_arg(settings.docker_exec_name)
    cli.add_arg("--context", docker_context)

    cli.add_arg("build")  # buildx build
    for label in default_labels:
        cli.add_arg("--label", label)
    for tag in tags:
        cli.add_arg("--tag", tag)
    if docker_file:
        cli.add_arg("--file", str(docker_file.absolute()))
    if push:
        cli.add_arg("--push")

    cli.add_arg(str(build_context))

    logger.debug(f'Building: "{" ".join(cli.commands)}"')

    logger.info(f"Building tag {tags[0]}")
    stdout, stderr, code = "", "", 0
    if not dry_run:
        stdout, stderr, code = await cli.run()
        if code:
            logger.error(f"Failed to build tag {tags[0]}:\n{stderr}")
            raise Exception(f"Failed to build tag {tags[0]}")
    logger.info(f"Finished building tag {tags[0]}")
    return stdout, stderr, code


async def get_images(labels: list[str] | None = None, docker_context: str = "default"):
    cli = CliInstance()
    cli.add_arg(settings.docker_exec_name)
    cli.add_arg("--context", docker_context)

    cli.add_arg("image")
    cli.add_arg("ls")
    cli.add_arg("-a")
    cli.add_arg("--format", "json")
    if labels:
        for label in labels:
            cli.add_arg("--filter", f"label={label}")

    stdout, stderr, code = await cli.run()
    if code:
        logger.error(f"Failed to get images:\n{stderr}")
    else:
        stdout = [loads(line) for line in stdout.split("\n")] if stdout else ""
    return stdout, stderr, code


async def remove_images(identifiers: list[str], docker_context: str = "default"):
    cli = CliInstance()
    cli.add_arg(settings.docker_exec_name)
    cli.add_arg("--context", docker_context)

    cli.add_arg("image")
    cli.add_arg("remove")
    for id in identifiers:
        cli.add_arg(id)

    logger.info(f"Removing images {identifiers}")
    stdout, stderr, code = await cli.run()
    if code:
        logger.error(f"Failed to remove image {identifiers}:\n{stderr}")
    logger.info(f"Removed images {identifiers} ({stdout})")

    return stdout, stderr, code


async def get_containers(
    labels: list[str] | None = None, docker_context: str = "default"
) -> tuple[list[dict] | str, str, int]:
    cli = CliInstance()
    cli.add_arg(settings.docker_exec_name)
    cli.add_arg("--context", docker_context)

    cli.add_arg("container")
    cli.add_arg("ls")
    cli.add_arg("-a")
    cli.add_arg("--format", "json")
    if labels:
        for label in labels:
            cli.add_arg("--filter", f"label={label}")

    stdout, stderr, code = await cli.run()
    if code:
        logger.error(f"Failed to get containers:\n{stderr}")
    else:
        stdout = [loads(line) for line in stdout.split("\n")] if stdout else ""
    return stdout, stderr, code


async def run_container(
    image: str,
    network: str | None = None,
    container_name: str | None = None,
    restart: str | None = None,
    labels: list[str] | None = None,
    pull: bool | None = True,
    docker_context: str = "default",
):
    cli = CliInstance()
    cli.add_arg(settings.docker_exec_name)
    cli.add_arg("--context", docker_context)

    cli.add_arg("run")
    cli.add_arg("--detach")
    if not restart:
        cli.add_arg("--rm")

    if network:
        cli.add_arg("--network", network)
    if container_name:
        cli.add_arg("--name", container_name)
    if restart:
        cli.add_arg("--restart", restart)
    if labels:
        for label in labels:
            cli.add_arg("--label", label)
    if pull is not None:
        cli.add_arg("--pull", "always" if pull else "never")

    cli.add_arg(image)

    logger.info(f"Starting container {image}")
    stdout, stderr, code = await cli.run()
    if code:
        logger.error(f"Failed to start container {image}:\n{stderr}")
    logger.info(f"Started container {image} ({stdout})")
    return stdout, stderr, code


async def stop_container(
    identifier: str, docker_context: str = "default", remove: bool = True
):
    cli = CliInstance()
    cli.add_arg(settings.docker_exec_name)
    cli.add_arg("--context", docker_context)

    cli.add_arg("container")
    cli.add_arg("stop")
    cli.add_arg(identifier)

    logger.info(f"Stopping container {identifier}")
    stdout, stderr, code = await cli.run()
    if code:
        logger.error(f"Failed to stop container {identifier}:\n{stderr}")
    logger.info(f"Stopped container {identifier} ({stdout})")

    if remove:
        await remove_container(identifier, docker_context)

    return stdout, stderr, code


async def remove_container(identifier: str, docker_context: str = "default"):
    cli = CliInstance()
    cli.add_arg(settings.docker_exec_name)
    cli.add_arg("--context", docker_context)

    cli.add_arg("container")
    cli.add_arg("rm")
    cli.add_arg(identifier)

    logger.info(f"Removing container {identifier}")
    stdout, stderr, code = await cli.run()
    if code:
        if stderr.startswith("Error response from daemon: No such container:"):
            logger.warning(f"No such container {identifier}")
        else:
            logger.error(f"Failed to remove container {identifier}:\n{stderr}")
    logger.info(f"Removed container {identifier} ({stdout})")

    return stdout, stderr, code


def gen_traefik_labels(
    subdomain_name: str, book_name: str, traefik_config: TraefikConfig
):
    return [
        f"traefik.http.services.{subdomain_name}.loadbalancer.server.port={traefik_config.port}",
        f"traefik.http.routers.{book_name}--{subdomain_name}.rule=Host(`{subdomain_name}.{book_name}.{traefik_config.base_domain}`)",
    ]
