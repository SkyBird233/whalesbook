import anyio
from .config import Book
from .services.cli_runner import CliInstance
from .services.registry import Registry, RegistryConfig
from . import docker
from typing import Any
from pydantic import (
    HttpUrl,
    BaseModel,
    model_validator,
    field_validator,
)
import logging
import re

logger = logging.getLogger(__name__)


class MainTag(BaseModel):
    registry_url: HttpUrl | None = None  # http[s]://HOST[:PORT]
    book_name_registry: str  # NAMESPACE/REPOSITORY
    subdomain_name: str | None = None  # TAG

    def to_string(self):
        string = self.book_name_registry
        if self.registry_url:
            port_str = (
                f":{self.registry_url.port}"
                if self.registry_url.port not in (80, 443)
                else ""
            )
            string = f"{self.registry_url.host}{port_str}/" + string
        if self.subdomain_name:
            string += f":{self.subdomain_name}"
        return string

    @field_validator("registry_url", mode="before")
    @classmethod
    def add_scheme(cls, value):
        if not value:
            return RegistryConfig().url
        if isinstance(value, str) and not (
            value.startswith("https://") or value.startswith("http://")
        ):
            return f"https://{value}"
        return value

    @model_validator(mode="before")
    @classmethod
    def validate(cls, data: Any):
        if isinstance(data, str):
            match = re.match(
                r"^(?:((?:https?:\/\/)?[a-zA-Z\d.-]+(?::[\d]+)?)\/)?([\w.-/]+\/[\w.-]+)(?::([\w.-]+))?$",
                data,
            )
            if not match:
                raise ValueError(f"Failed to validate main tag string {data}")
            return dict(
                zip(
                    (
                        "registry_url",
                        "book_name_registry",
                        "subdomain_name",
                    ),
                    match.groups(),
                )
            )
        return data


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


async def get_new_refs(registry: Registry, book: Book):
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
    registry_url: HttpUrl,
    book: Book,
    ref_pairs_to_update: set[tuple[str, str]],
    dry_run: bool = False,
):
    ref_pair_dicts_to_update = {
        ref_pair[1]: ref_pair[0] for ref_pair in ref_pairs_to_update
    }

    tag_name = MainTag(
        registry_url=registry_url, book_name_registry=book.name_registry
    ).to_string()

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


async def delete_old_images(registry: Registry, book: Book):
    tracking_ref_pairs = await get_tracking_ref_pairs(book)
    tracking_main_tags = [
        MainTag(
            registry_url=registry.url,
            book_name_registry=book.name_registry,
            subdomain_name=ref_pair[1],
        ).to_string()
        for ref_pair in tracking_ref_pairs
    ]
    tracking_git_tags = [f"git-{ref_pair[0]}" for ref_pair in tracking_ref_pairs]

    # registry
    registry_tags = await registry.get_tags(book.name_registry)
    for tag in registry_tags:
        if tag.startswith("git-") and tag not in tracking_git_tags:
            try:
                await registry.delete_by_tag(book.name_registry, tag)
            except Exception as e:
                logger.error(e)

    # builder & runner
    for context in (book.builder, book.runner):
        images, stderr, code = await docker.get_images(
            labels=[f"whalesbook.main_tag={tag}" for tag in tracking_main_tags],
            docker_context=context,
        )
        if code:
            continue
        image_ids = set(
            image["ID"]  # type: ignore
            for image in images
            if image["Tag"].startswith("git-") and image["Tag"] not in tracking_git_tags  # type: ignore
        )
        if image_ids:
            await docker.remove_images(
                identifiers=list(image_ids), docker_context=context
            )
        else:
            logger.info(f"No images to remove for docker context {context}")


async def get_containers_for_book(registry_url: HttpUrl, book: Book):
    image_prefix = MainTag(
        registry_url=registry_url, book_name_registry=book.name_registry
    ).to_string()

    containers, stderr, code = await docker.get_containers(
        labels=["whalesbook.main_tag"], docker_context=book.runner
    )
    if code:
        raise Exception("Failed to get current containers")

    containers = (
        container
        for container in containers
        if image_prefix in container["Image"]  # type:ignore
    )
    logger.debug(f"Current containers for book {book.name}: {containers}")
    return containers


async def update_containers(registry: Registry, book: Book):
    # Get current (old) containers
    old_containers = await get_containers_for_book(registry.url, book)

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
                    MainTag(
                        registry_url=registry.url,
                        book_name_registry=book.name_registry,
                        subdomain_name=tag,
                    ).to_string(),
                    book.docker_network,
                    None,
                    "always",
                    labels,
                    True,
                    book.runner,
                )

    # Remove old containers
    if old_containers:
        async with anyio.create_task_group() as tg:
            for container in old_containers:
                tg.start_soon(docker.stop_container, container["ID"], book.runner)  # type: ignore


async def stop_containers(registry_url: HttpUrl, book: Book):
    old_containers = await get_containers_for_book(registry_url, book)

    for container in old_containers:
        await docker.stop_container(container["ID"])  # type: ignore


async def update_book(registry: Registry, book: Book, force: bool = False):
    ref_pairs_to_update, outdated_registry_hashes = await get_new_refs(registry, book)
    if not ref_pairs_to_update and not force:
        logger.info(f"Nothing to update for book {book.name}")
        return
    if force:
        logger.info(f"Forceing update for book {book.name}")
    await update_images(registry.url, book, ref_pairs_to_update, dry_run=False)
    await update_containers(registry, book)
