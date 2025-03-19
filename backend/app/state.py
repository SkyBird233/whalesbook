import anyio
from app.config import Book
from app.services.cli_runner import CliInstance
from app.services.registry import Registry
from app import docker
from pydantic import AnyUrl
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


async def ls_remote(repo_url: str) -> list[tuple[str, str]]:
    cli = CliInstance()
    cli.add_arg("git")
    cli.add_arg("ls-remote")
    cli.add_arg(repo_url)

    logger.info(f"Fetching refs from {repo_url}")
    stdout, stderr, code = await cli.run()
    if code:
        raise Exception("ls-remote failed", stdout, stderr, code)
    return [tuple(line.split()) for line in stdout.split("\n")]  # type: ignore


async def get_tracking_ref_pairs(book: Book):
    tracking_ref_pairs: set[tuple[str, str]] = set()
    for repo in book.repos:
        tracking_refs_names = [ref.name for ref in repo.refs]
        repo_refs_all = await ls_remote(repo.url)
        tracking_ref_pairs.update(
            [item for item in repo_refs_all if item[1] in tracking_refs_names]
        )
    return tracking_ref_pairs


async def get_new_refs(book: Book, registry: Registry):
    outdated_registry_hashes: set[str] = set()
    ref_pairs_to_update: set[tuple[str, str]] = set()

    # Old hashes from registry
    registry_repo_tags = (
        await registry.get_tags(book.name_registry)
        if book.name_registry in registry.repositories
        else []
    )
    registry_hashes = [tag for tag in registry_repo_tags if not tag.startswith("git-")]

    # Git remote
    tracking_ref_pairs: set[tuple[str, str]] = await get_tracking_ref_pairs(book)
    logger.debug(f"tracking_ref_pairs: {tracking_ref_pairs}")

    ref_name_to_subdomain_name = {
        ref.name: ref.subdomain_name for repo in book.repos for ref in repo.refs
    }  # subdomain name == registry repo tag
    for ref_pair in tracking_ref_pairs:
        if (
            ref_name_to_subdomain_name[ref_pair[1]] not in registry_repo_tags
            or f"git-{ref_pair[0]}" not in registry_repo_tags
        ):
            ref_pairs_to_update.add(ref_pair)

    all_hashes = [ref[0] for ref in tracking_ref_pairs]
    for registry_hash in registry_hashes:
        if registry_hash.replace("git-", "") not in all_hashes:
            outdated_registry_hashes.add(registry_hash)

    logger.debug(f"ref_pairs_to_update: {ref_pairs_to_update}")

    return ref_pairs_to_update, outdated_registry_hashes


async def update_images(
    registry_url: AnyUrl,
    book: Book,
    ref_pairs_to_update: set[tuple[str, str]],
    dry_run: bool = False,
):
    ref_pair_dicts_to_update = {
        ref_pair[1]: ref_pair[0] for ref_pair in ref_pairs_to_update
    }

    tag_name = f"{urlparse(str(registry_url)).netloc}/{book.name_registry}"

    async with anyio.create_task_group() as tg:
        for repo in book.repos:
            for ref in repo.refs:
                if ref.name not in ref_pair_dicts_to_update.keys():
                    continue
                tg.start_soon(
                    docker.build_image,
                    [
                        f"{tag_name}:{ref.subdomain_name}",
                        f"{tag_name}:git-{ref_pair_dicts_to_update[ref.name]}",
                    ],
                    f"{repo.url}#{ref_pair_dicts_to_update[ref.name]}",
                    book.builder,
                    book.docker_file,
                    True,
                    dry_run,
                )


async def rebuild_tracking_images(
    registry_url: AnyUrl,
    book: Book,
    dry_run: bool = False,
):
    ref_pairs_to_update = await get_tracking_ref_pairs(book)
    await update_images(registry_url, book, ref_pairs_to_update, dry_run)


async def delete_old_images(book_name, git_hashes):
    # registry & builder & runner?
    pass


async def update_containers(registry: Registry, book: Book):
    # Get current (old) containers
    image_prefix = f"{urlparse(str(registry.url)).netloc}/{book.name_registry}"
    old_containers, stderr, code = await docker.get_containers(
        labels=["whalesbook.main_tag"], docker_context=book.runner
    )
    if code:
        raise Exception("Failed to get current containers")
    logger.debug(f"Current containers for book {book.name}: {old_containers}")

    # Start new containers first
    book_repo_refs = {
        ref.name: ref.subdomain_name for repo in book.repos for ref in repo.refs
    }
    logger.debug(f"book_repo_refs: {book_repo_refs}")
    async with anyio.create_task_group() as tg:
        for tag in await registry.get_tags(
            book.name_registry
        ):  # registry tag == subdomain name
            if tag in book_repo_refs.values():
                labels = book.custom_labels.copy()
                if book.traefik_config:
                    labels.extend(
                        docker.gen_traefik_labels(tag, book.name, book.traefik_config)
                    )
                tg.start_soon(
                    docker.run_container,
                    f"{image_prefix}:{tag}",
                    None,
                    None,
                    None,
                    labels,
                    True,
                    book.runner,
                )

    # Remove old containers
    if old_containers:
        async with anyio.create_task_group() as tg:
            for container in old_containers:
                tg.start_soon(docker.stop_container, container["ID"], book.runner)  # type: ignore


async def stop_containers(book):
    old_containers, stderr, code = await docker.get_containers(
        labels=["whalesbook.main_tag"], docker_context=book.runner
    )
    if code:
        raise Exception("Failed to get current containers")
    logger.info(f"Current containers for book {book.name}: {old_containers}")

    for container in old_containers:
        await docker.stop_container(container["ID"])  # type: ignore


async def update_book(book: Book, registry: Registry):
    ref_pairs_to_update, outdated_registry_hashes = await get_new_refs(book, registry)
    await update_images(registry.url, book, ref_pairs_to_update, dry_run=False)
    await update_containers(registry, book)
