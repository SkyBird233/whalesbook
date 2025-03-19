# Setup test environment

## 1. Generate certs
> https://distribution.github.io/distribution/about/insecure/#use-self-signed-certificates

```shell
mkdir -p certs

openssl req \
  -newkey rsa:4096 -nodes -sha256 -keyout certs/domain.key \
  -addext "subjectAltName = DNS:registry" \
  -x509 -days 365 -out certs/domain.crt
```

Copy the domain.crt file to `/etc/docker/certs.d/registry:5000/ca.crt`


## 2. Edit hosts
```text
# /etc/hosts
...
127.0.0.1   registry
```

# Test
```shell
docker compose up --build
```

# Cleanup
```shell
docker compose down
docker image ls --filter "label=whalesbook.build_context" --format "{{.ID}}" | xargs -r docker image rm -f
```
- Edit `/etc/hosts` to remove previously added entry
- Remove `/etc/docker/certs.d/registry:5000/ca.crt`

# TODO
- Use docker in docker for tests