# Docker Essentials

Docker packages an application and its dependencies into a portable image that
runs as a container on any host with a container runtime.

## Core concepts
- **Image**: an immutable, layered filesystem snapshot built from a `Dockerfile`.
- **Container**: a running (or stopped) instance of an image.
- **Registry**: stores and distributes images (Docker Hub, Amazon ECR, GHCR).
- **Layer**: each instruction in a `Dockerfile` creates a cached layer. Order
  instructions from least- to most-frequently changing to maximize cache reuse.

## Common commands
- Build: `docker build -t myapp:1.0 .`
- Run: `docker run -d -p 8000:8000 --env-file .env myapp:1.0`
- List containers: `docker ps -a`
- Logs: `docker logs -f <container>`
- Exec into a container: `docker exec -it <container> sh`
- Remove dangling images: `docker image prune -f`

## Dockerfile best practices
- Use a small base image (e.g. `python:3.12-slim`) to reduce size and attack surface.
- Use multi-stage builds to keep build tools out of the final image.
- Copy dependency manifests and install before copying source so dependency
  layers stay cached when only source changes.
- Run as a non-root user with `USER appuser`.
- Add a `HEALTHCHECK` so orchestrators know when the app is ready.
- Use `.dockerignore` to keep build context small.

## Multi-stage build example
```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER 1000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting
- "Cannot connect to the Docker daemon": the daemon/service is not running.
- Image too large: check layers with `docker history <image>` and prune build deps.
- Container exits immediately: inspect `docker logs`; the main process likely crashed.
