# CI/CD with GitHub Actions

Continuous Integration (CI) builds and tests every change; Continuous Delivery/
Deployment (CD) ships passing changes to an environment automatically.

## Pipeline stages (typical)
1. **Lint** — static checks (ruff, eslint).
2. **Test** — unit/integration tests (pytest).
3. **Build** — produce a Docker image.
4. **Push** — push the image to a registry (ECR/GHCR).
5. **Deploy** — roll the new image out to the target environment.

## GitHub Actions concepts
- **Workflow**: a YAML file in `.github/workflows/` triggered by events.
- **Job**: a set of steps running on a runner; jobs run in parallel unless `needs`
  creates a dependency.
- **Step**: a single command or reusable `action`.
- **Secret**: encrypted value injected at runtime (`${{ secrets.NAME }}`).
- **OIDC**: lets a workflow assume an AWS IAM role without storing static keys.

## Minimal CI example
```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: pytest -q
```

## Deployment strategies
- **Rolling**: replace instances gradually; default for Kubernetes Deployments.
- **Blue/Green**: stand up a new environment, switch traffic, keep old for rollback.
- **Canary**: send a small % of traffic to the new version before full rollout.

## Good practices
- Keep secrets in the CI secret store, never in the repo.
- Make `main` protected: require CI to pass before merge.
- Tag images with the commit SHA for traceability and easy rollback.
- Cache dependencies to speed up builds.
