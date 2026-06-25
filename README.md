# DevOps Docs RAG Assistant

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about
**Docker, Kubernetes, Terraform, AWS, CI/CD, and Git**, grounded in a curated
knowledge base. Built primarily to demonstrate an end-to-end **DevOps / cloud
deployment** workflow — IaC, containers, CI/CD, and observability — on the AWS
Free Tier.

> RAG pipeline: **Voyage AI** embeddings + **FAISS** vector search + **Groq**
> (Llama 3.3) generation. Served by **FastAPI**, containerized with **Docker**,
> provisioned with **Terraform**, deployed by **GitHub Actions** to **EC2**, with
> logs and alarms in **CloudWatch**.

---

## Architecture

```
                 ┌──────────────┐      OIDC (no static keys)
   git push ───▶ │ GitHub       │ ───────────────────────────┐
                 │ Actions CI/CD│                             ▼
                 └──────┬───────┘                      ┌─────────────┐
                        │ build + push image           │   AWS IAM   │
                        ▼                               └─────────────┘
                 ┌──────────────┐   ssm send-command          │
                 │  Amazon ECR  │ ◀───────────┐               │ assume role
                 └──────┬───────┘             │               ▼
                        │ docker pull   ┌──────┴──────────────────────┐
                        ▼               │  EC2 t3.micro (Free Tier)    │
                 ┌──────────────┐       │  ┌────────────────────────┐  │
   user  ─HTTP─▶ │ Security Grp │ ─────▶│  │ Docker: FastAPI app    │  │
                 │  (port 80)   │       │  │  /  → chat UI          │  │
                 └──────────────┘       │  │  /api/chat → RAG       │  │
                                        │  └─────────┬──────────────┘  │
                                        └────────────┼─────────────────┘
                                                     │ logs/metrics
                          ┌──────────────┐           ▼
   Voyage AI (embeddings) ◀── RAG query ── ┌──────────────────┐
   Groq (LLM generation)  ◀──────────────  │   CloudWatch     │
                                           │ logs + alarms    │
                                           └──────────────────┘
```

### Request flow
1. User asks a question in the web UI (`/`).
2. `/api/chat` embeds the question via **Voyage AI**.
3. **FAISS** returns the top-K most similar doc chunks (cosine similarity).
4. The chunks + question are sent to **Groq (Llama 3.3)** with a grounded prompt.
5. The answer and its source chunks are returned to the UI.

The FAISS index is built from `data/*.md` by `app/ingest.py` (runs at container
start). The embeddings API keeps the image small — no `torch` is bundled.

---

## Tech stack

| Layer            | Choice                                  | Why |
|------------------|-----------------------------------------|-----|
| LLM              | Groq (Llama 3.3 70B), free tier         | Free, fast |
| Embeddings       | Voyage AI `voyage-3-lite`, free tier    | Lightweight, no local model |
| Vector store     | FAISS (`IndexFlatIP`)                    | In-process, no DB to run |
| API / UI         | FastAPI + Jinja2 + vanilla JS           | Minimal, single container |
| Container        | Docker (`python:3.12-slim`, non-root)   | Portable, small |
| IaC              | Terraform (AWS provider)                 | Reproducible infra |
| CI/CD            | GitHub Actions (OIDC, no static keys)    | Lint/test + build/push/deploy |
| Compute          | EC2 `t3.micro` (Free Tier)               | ~$0 for 12 months |
| Registry         | Amazon ECR (lifecycle policy)            | Private images |
| Deploy mechanism | SSM RunCommand (no inbound SSH)          | Secure, keyless |
| Observability    | CloudWatch logs + alarms + CW agent      | Logs, CPU/status/mem |

---

## Repository layout

```
app/                FastAPI app + RAG pipeline
  main.py           HTTP endpoints (/, /health, /api/chat)
  config.py         Env-based settings (pydantic-settings)
  ingest.py         Build the FAISS index from data/
  rag/              embeddings, vectorstore, llm, chunking, pipeline
  templates/        chat UI
data/               Knowledge-base markdown (Docker, K8s, Terraform, AWS, CI/CD, Git)
tests/              pytest (no external APIs needed)
terraform/          AWS infra: VPC/SG, ECR, EC2, IAM, SSM, CloudWatch, OIDC
.github/workflows/  ci.yml (lint/test/build), deploy.yml (build→push→deploy)
Dockerfile          Multi-stage-friendly, non-root, healthcheck
docker-compose.yml  Local run
Makefile            Common tasks
```

---

## Run locally

Prereqs: Python 3.12 (or 3.11), a free [Groq key](https://console.groq.com/keys)
and [Voyage key](https://dashboard.voyageai.com/).

```bash
cp .env.example .env          # then fill in GROQ_API_KEY and VOYAGE_API_KEY
make dev                      # install deps (or: pip install -r requirements-dev.txt)
make ingest                   # build the FAISS index from data/
make run                      # http://localhost:8000
```

Or with Docker:

```bash
docker compose up --build     # reads .env, builds index on start
```

Quality checks:

```bash
make lint      # ruff
make test      # pytest
```

---

## Deploy to AWS (Free Tier)

### Prerequisites (one-time)
1. AWS account + AWS CLI configured locally with admin (for the first `apply`).
2. Terraform >= 1.5.
3. **GitHub OIDC provider** in your AWS account (account-global, create once):
   ```bash
   aws iam create-open-id-connect-provider \
     --url https://token.actions.githubusercontent.com \
     --client-id-list sts.amazonaws.com \
     --thumbprint-list 1c58a3a8518e8759bf075b76b750d4f2df264fcd
   ```
   (Skip if it already exists — Terraform looks it up.)

### Provision infrastructure
```bash
cd terraform
cp example.tfvars terraform.tfvars   # fill in keys + set github_repo = "owner/repo"
terraform init
terraform apply
```

Terraform creates the ECR repo, EC2 instance (Docker + CloudWatch agent via
user-data), IAM roles, SSM SecureString params for the API keys, CloudWatch log
group + alarms, and the GitHub Actions OIDC deploy role.

Outputs:
- `app_url` — the public URL once the first image is deployed.
- `ecr_repository_url`, `instance_id`, `log_group`.
- `github_actions_role_arn` — use it in the next step.

### Wire up CI/CD
In the GitHub repo settings → **Secrets and variables → Actions**:
- Add **secret** `AWS_DEPLOY_ROLE_ARN` = the `github_actions_role_arn` output.
- Add **variable** `DEPLOY_ENABLED` = `true` to turn the deploy job on. (Until
  then the `deploy` job is skipped, so the repo stays green before AWS exists.)

If your region/repo/project name differ from defaults, update the `env:` block in
[`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).

### Ship it
Push to `main`. The `deploy` workflow:
1. assumes the AWS role via OIDC,
2. builds the image and pushes `:<sha>` and `:latest` to ECR,
3. runs `deploy-app.sh` on the instance via **SSM RunCommand** (pull + restart),
4. waits for success.

Visit `app_url`. Logs stream to CloudWatch (`/devops-rag/app`).

### Tear down
```bash
cd terraform && terraform destroy
```

---

## Cost notes (staying ~$0)
- EC2 `t3.micro`: 750 hrs/month free for 12 months — one always-on instance fits.
- ECR: a few small images; lifecycle policy keeps only the last 5.
- CloudWatch: 7-day log retention; a couple of alarms (free tier covers 10).
- Groq + Voyage: free tiers cover demo traffic.
- Recommended: set an **AWS Budgets** alert at $1, and `terraform destroy` /
  stop the instance when not demoing.

> ⚠️ The default security group exposes port 80 to `0.0.0.0/0`. Set
> `allow_http_cidr` to your IP in `terraform.tfvars` to lock it down.

---

## What this demonstrates (CV talking points)
- **IaC**: full AWS environment defined in Terraform, reproducible from scratch.
- **CI/CD**: GitHub Actions with lint/test gates and keyless **OIDC** deploys.
- **Containers**: small, non-root image with a healthcheck.
- **Secure deploys**: no inbound SSH, no static cloud keys; secrets in SSM.
- **Observability**: centralized logs + CPU/status/memory alarms.
- **Cost engineering**: deliberately architected for the AWS Free Tier.
- **Applied GenAI**: a practical RAG pipeline with source attribution.

### Swap the knowledge base
Drop your own `.md`/`.txt` files into `data/`, re-run `make ingest` (or redeploy),
and the bot answers over your content — no code changes required.
