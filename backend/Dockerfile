FROM alpine:3

RUN apk add --no-cache python3~3.12 docker-cli docker-cli-buildx uv git curl

WORKDIR /app
COPY pyproject.toml .python-version uv.lock ./
RUN uv sync --frozen --no-cache

COPY . /app
RUN uv pip install -e .

CMD ["/app/.venv/bin/python", "app/main.py"]