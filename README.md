# whalesbook

A simple tool for building and deploying Git repository branches as containerized applications. It leverages Git, Docker, and Traefik to automate the build and deployment pipeline, focusing on simplicity.

## Why

This project is inspired by Cloudflare Pages: it automatically deploys builds on branches with custom configuration and serves them on a subdomain. However, Cloudflare Pages currently supports neither Docker containers, grouping repositories, nor public dashboards. This project aims to fill these gaps while keeping the core workflow similar.

## Core Concepts

- **Book**: A collection of repositories and configuration that defines an application or service.
- **Repo**: A Git repository tracked as part of a book.
- **Ref**: A Git reference (branch or tag) to build and deploy.

### Status & Lifecycle

- Status is derived directly from the configuration, Git state, Docker CLI, and registry.
- Containers are built using Docker Buildx, which supports Git contexts.
- Container management relies on Docker's restart policy; deployed containers remain running as long as Docker and Traefik are active.

### Domain Naming

- The default domain format is: `ref-name.book-name.base-domain`.

### Image Tagging & Labels

- Images are tagged as `<book.name>:<subdomain_name>` and `<book.name>:git-<git_hash_full>`.
- Image labels:
  - `whalesbook.build_context`: The exact build context used for Docker Buildx.
  - `whalesbook.git_tag`: Example: `registry.example.com/library/myrepo:git-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
  - `whalesbook.main_tag`: Main image tag, e.g., `registry.example.com/library/myrepo:main`

## Quick Start

1. **Clone the repository**

  ```sh
  git clone https://github.com/yourname/whalesbook.git
  cd whalesbook
  ```

2. **Configure your books**

  Edit or create `config/config.yml` to define your books, repositories, and refs.

  Edit `compose.yml`.

  Note that you need a registry for storing images.

3. **Start the backend and frontend**

  ```sh
  docker compose up -d -b && docker compose logs -f
  ```

## Configuration

Configuration is managed via a YAML file (default: `config/config.yml`). Example:

```yaml
docker_registry:
  url: https://registry.example.com
  username: username
  password: password

schedule:
  cron: "*/5 * * * *"

books:
  - name: mybook
    repos:
      - name: main
        url: https://github.com/username/repo.git
        refs:
          - main
          - name: dev
            subdomain_name: develop
          - feat-some-feat
      - name: myrepo
        url: https://mygit.example.com/username/repo.git
        refs:
          - fix-some-fix
    docker_file: Dockerfile
    traefik_config:
      base_domain: example.com
      port: 80
      cert_resolver: myresolver
    docker_network: traefik_reverse_proxy
```

### Book

- `name`: Name of the book.
- `name_registry`: Docker image name (defaults to `library/<name>`).
- `repos`: List of repositories (see below).
- `docker_file`: Path to Dockerfile, relative to `config.yml` (optional).
- `builder`: Docker context name, defaults to `default`.
- `runner`: Same as above, but for runner.
- `traefik_config`
  - `base_domain`: example.com
  - `port`: The port the service inside the container listens on
  - `cert_resolver`: Certificate resolver name configured in Traefik's static config.
- `custom_labels`: Docker labels other than generated Traefik labels. Can be used with generated labels but currently not dynamic.
- `docker_network`: Docker network to join.

### Repo

- `name`: Name of the repo.
- `url`: Git URL. Not only GitHub, as Git is used to interact with it.
- `refs`: List of refs ("refs/*" theoretically) to track.

### Ref

- `name`: Name of the ref (e.g., `main` or `refs/heads/main`).
- `subdomain_name`: Subdomain name for this ref (optional, auto-generated).
