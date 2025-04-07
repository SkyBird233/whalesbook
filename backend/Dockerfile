FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1

WORKDIR /app

RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable --no-dev

ADD . /app

RUN uv sync --frozen --no-editable --no-dev


FROM python:3.12-alpine

RUN apk add --no-cache docker-cli docker-cli-buildx git

COPY --from=builder /app/.venv /app/.venv

CMD ["/app/.venv/bin/whalesbook"]