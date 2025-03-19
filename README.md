

# TODO

- docker connect to registry in compose
  - dind or
  - cert with basic auth
- read from ~/.docker/config ?
  - or use docker inspect to replace registry.py?
- catch build failures (upload failed?)
- tests passed



# config

## book
name


### ref

name: main

name: refs/heads/main
subdomain name: main
docker image tag:
- book.name:subdomain_name
- book.name:git-{git_hash_full}

