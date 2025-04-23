# whalesbook Backend

It is recommended to use `compose.yml` in the root directory. However, if you only need the backend or CLI, follow the instructions below.

## Setup

1. Install `uv` and Docker.
2. Install dependencies:
   ```sh
   uv sync --frozen
   ```
3. Configure `../config/config.yml` for your registry and books.

## Usage

- To run the API server:
  ```sh
  uv run whalesbook --config-file ../config/config.yml serve
  ```
- To use the CLI:
  ```sh
  uv run whalesbook --config-file ../config/config.yml --help
  ```
- With Docker:
  Build the container using `Dockerfile` or `dev.Dockerfile`.

## Tests

See [tests/README.md](./tests/README.md) for test environment setup.
