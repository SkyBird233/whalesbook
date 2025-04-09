from fastapi import FastAPI, APIRouter, HTTPException, Response
from fastapi.routing import APIRoute
from contextlib import asynccontextmanager
from .schedule import scheduler, schedule_books
from .services.registry import create_registry
from . import config
from .state import RefState, get_refs_state


@asynccontextmanager
async def lifespan(app: FastAPI):
    reg = await create_registry(config.settings.docker_registry)  # type: ignore
    schedule_books(config.settings.schedule.cron, reg, config.settings.books)
    yield
    scheduler.shutdown()


def generate_unique_id(route: APIRoute):
    return route.name


fastapi_options = {"root_path": "/api/v1", "lifespan": lifespan}

router = APIRouter(
    generate_unique_id_function=generate_unique_id,
)


@router.get("/", status_code=200)
async def health_check() -> Response:
    return Response(status_code=200)


@router.get("/books")
async def get_books() -> list[config.Book]:
    return config.settings.books


@router.get("/books/{book_name}")
async def get_book(book_name: str) -> config.Book:
    book = tuple(book for book in config.settings.books if book.name == book_name)
    if not book:
        raise HTTPException(404, f"Book {book_name} not found")
    return book[0]


@router.get("/books/{book_name}/state")
async def get_book_state(book_name: str) -> dict[str, dict[str, RefState]]:
    book = await get_book(book_name)
    return await get_refs_state(
        config.settings.docker_registry.url,  # type:ignore
        book,
    )
