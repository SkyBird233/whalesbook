from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from .schedule import scheduler, schedule_books
from .services.registry import create_registry
from . import config
from .state import get_containers_for_book, MainTag


@asynccontextmanager
async def lifespan(app: FastAPI):
    reg = await create_registry(config.settings.docker_registry)  # type: ignore
    schedule_books(config.settings.schedule.cron, reg, config.settings.books)
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan, root_path="/api/v1")
# app = FastAPI(root_path="/api/v1")


@app.get("/", status_code=200)
async def health_check() -> None:
    return


@app.get("/books")
async def list_books() -> list[str]:
    return [book.name for book in config.settings.books]


@app.get("/books/{book_name}")
async def get_book(book_name: str) -> config.Book:
    book = tuple(book for book in config.settings.books if book.name == book_name)
    if not book:
        raise HTTPException(404, f"Book {book_name} not found")
    return book[0]


class ContainerOut(BaseModel):
    subdomain_name: str
    base_domain: str | None = None
    build_context: str


@app.get("/books/{book_name}/containers")
async def get_book_containers(book_name: str) -> list[ContainerOut]:
    book = await get_book(book_name)
    containers_raw = await get_containers_for_book(
        config.settings.docker_registry.url,  # type:ignore
        book,
    )

    containers = []
    for container in containers_raw:
        labels = {
            k: v
            for label in container["Labels"].split(",")  # type:ignore
            for k, v in [label.split("=", maxsplit=1)]
        }
        containers.append(
            ContainerOut(
                subdomain_name=MainTag.model_validate(
                    labels["whalesbook.main_tag"]
                ).subdomain_name
                or "",
                base_domain=f"{book.name}.{book.traefik_config.base_domain}"
                if book.traefik_config
                else None,
                build_context=labels["whalesbook.build_context"],
            )
        )
    return containers
