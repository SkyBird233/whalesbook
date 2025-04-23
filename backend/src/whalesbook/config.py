from pydantic import BaseModel, field_validator, model_validator
from pathlib import Path
from pydantic_settings import (
    BaseSettings,
    YamlConfigSettingsSource,
)
import re
from .services.registry import RegistryConfig
from typing import Any


class Ref(BaseModel):
    name: str
    subdomain_name: str | None = None

    @model_validator(mode="after")
    def serialize_names(self):
        if not self.subdomain_name:
            self.subdomain_name = self.name
        self.subdomain_name = self.subdomain_name.lower()
        self.subdomain_name = re.sub(r"[^a-z0-9-]", "-", self.subdomain_name)
        self.subdomain_name = re.sub(r"-+", "-", self.subdomain_name)
        self.subdomain_name = self.subdomain_name[:63].strip("-")

        self.name = (
            self.name if self.name.startswith("refs/") else f"refs/heads/{self.name}"
        )

        return self


class Repo(BaseModel):
    name: str
    url: str = "https://github.com/username/repo.git"  # End with .git
    refs: list[Ref] = [Ref(name="main")]  # default to refs/heads/<name>; full ref `refs/xxx/...`

    @field_validator("refs", mode="before")
    @classmethod
    def serialize_refs(cls, refs: Any):
        if not isinstance(refs, list):
            refs = [refs]
        new_refs = [
            Ref.model_validate(ref) if isinstance(ref, dict) else Ref(name=ref)
            for ref in refs
        ]
        return new_refs


class TraefikConfig(BaseModel):
    base_domain: str = "localhost"
    port: int = 80
    cert_resolver: str = "myresolver"


class Book(BaseModel):
    name: str
    name_registry: str = ""  # library/default_book, as docker image name
    repos: list[Repo] = [Repo(name="main")]
    docker_file: Path | None = None
    builder: str = "default"  # existing docker context
    runner: str = "default"
    traefik_config: TraefikConfig | None = TraefikConfig()
    custom_labels: list[str] = []
    docker_network: str | None = None

    @model_validator(mode="after")
    def serialize_name(self):
        if not self.name_registry:
            self.name_registry = (
                self.name if "/" in self.name else f"library/{self.name}"
            )
        return self

    # TODO builder and runner validation


class SchedulerConfig(BaseModel):
    cron: str = "*/5 * * * *"


class Settings(BaseSettings):
    config_dir: Path = Path("config")
    docker_exec_name: str = "docker"

    # TODO setup contexts
    docker_contexts: list[str] = ["default"]

    docker_registry: RegistryConfig | None = None

    schedule: SchedulerConfig = SchedulerConfig()

    books: list[Book] = [Book(name="default_book")]

    @model_validator(mode="after")
    def update_path(self):
        for book in self.books:
            if book.docker_file:
                book.docker_file = self.config_dir / book.docker_file
        return self

    # FIXME: https://github.com/pydantic/pydantic-settings/issues/259 (Why??)
    @classmethod
    def from_yaml(cls, path: Path | None = None):
        if not path:
            path = Path(cls().config_dir / "config.yml")
        return cls(
            **dict(YamlConfigSettingsSource(cls, path)(), config_dir=path.parent)
        )


settings = Settings()

if __name__ == "__main__":
    import os

    print(os.getcwd())
    print(settings.from_yaml().model_dump_json(indent=2))
