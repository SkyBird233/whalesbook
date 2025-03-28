FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

RUN apk add --no-cache docker-cli docker-cli-buildx git

WORKDIR /app

RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ADD . /app

RUN uv sync --frozen

CMD [ "/app/.venv/bin/whalesbook" ]