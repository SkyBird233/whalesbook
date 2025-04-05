from fastapi import FastAPI, HTTPException, Response
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


app = FastAPI(
    lifespan=lifespan,
    root_path="/api/v1",
    generate_unique_id_function=generate_unique_id,
)


@app.get("/", status_code=200)
async def health_check() -> Response:
    return Response(status_code=200)


@app.get("/books")
async def get_books() -> list[config.Book]:
    return config.settings.books


@app.get("/books/{book_name}")
async def get_book(book_name: str) -> config.Book:
    book = tuple(book for book in config.settings.books if book.name == book_name)
    if not book:
        raise HTTPException(404, f"Book {book_name} not found")
    return book[0]


@app.get("/books/{book_name}/state")
async def get_book_state(book_name: str) -> dict[str, dict[str, RefState]]:
    book = await get_book(book_name)
    return await get_refs_state(
        config.settings.docker_registry.url,  # type:ignore
        book,
    )
