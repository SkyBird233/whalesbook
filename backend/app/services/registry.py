import ssl
from typing import Any
from pathlib import Path
from httpx import AsyncClient, BasicAuth
from pydantic import BaseModel, HttpUrl, field_validator
from urllib import parse
import logging

logger = logging.getLogger(__name__)


class RegistryConfig(BaseModel):
    url: HttpUrl
    username: str | None = None  # TODO: from docker config or manually login
    password: str | None = None
    cafile: Path | None = None

    @field_validator("url", mode="before")
    @classmethod
    def validate_url(cls, url: Any):
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return f"https://{url}"


class Registry:
    def __init__(self, registry_config: RegistryConfig):
        self.api_version = "v2"
        self.url = registry_config.url
        self._base_url = parse.urljoin(str(registry_config.url) + "/", self.api_version)
        self._username = registry_config.username
        self._password = registry_config.password
        self._cafile = registry_config.cafile
        self.client: AsyncClient 
        self.repositories: list[str] = []

    async def init(self):
        self.client = AsyncClient(
            base_url=str(self._base_url),
            auth=(
                BasicAuth(username=self._username, password=self._password)
                if self._username and self._password
                else None
            ),
            verify=ssl.create_default_context(cafile=self._cafile)
            if self._cafile
            else True,
        )
        await self.update_catalog()

    async def update_catalog(self) -> list[str]:
        resp = await self.client.get("_catalog")
        if not resp.status_code == 200:
            raise Exception("Failed to get catalog", resp.status_code, resp.url)
        self.repositories = resp.json()["repositories"]
        return self.repositories

    async def get_tags(self, repository: str) -> list[str]:
        resp = await self.client.get(f"{repository}/tags/list")
        if not resp.status_code == 200:
            raise Exception("Failed to get tags", resp.status_code, repository)
        return resp.json()["tags"]

    async def delete_by_tag(self, repository: str, tag: str):
        tag_manifest = await self.client.get(
            f"{repository}/manifests/{tag}",
            headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"},
        )
        digest = tag_manifest.headers["docker-content-digest"]

        delete_result = await self.client.delete(f"{repository}/manifests/{digest}")
        if not delete_result.status_code == 202:
            raise Exception(f"Failed to delete {repository}:{tag}\n\tDigest: {digest}")


async def create_registry(registry_config: RegistryConfig):
    registry = Registry(registry_config)
    await registry.init()
    return registry
