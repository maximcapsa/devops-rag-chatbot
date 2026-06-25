# AWS Core Services for DevOps

## Compute
- **EC2**: virtual machines. `t3.micro`/`t2.micro` are Free Tier eligible
  (750 hours/month for the first 12 months on a new account).
- **Lambda**: serverless functions; always-free tier of 1M requests/month.
- **ECS / Fargate**: run containers. Fargate is serverless (no EC2 to manage) but
  is not Free Tier eligible.

## Networking
- **VPC**: isolated virtual network. A **Security Group** is a stateful virtual
  firewall attached to instances; rules are allow-only.
- Open only the ports you need (e.g. 22 for SSH from your IP, 80/443 for web).
- Prefer **AWS Systems Manager (SSM) Session Manager** over opening SSH (port 22)
  to the internet — it gives shell access through IAM without inbound ports.

## Containers & registry
- **ECR**: private Docker registry. Authenticate the Docker CLI with:
  ```
  aws ecr get-login-password --region <region> \
    | docker login --username AWS --password-stdin <acct>.dkr.ecr.<region>.amazonaws.com
  ```

## Identity
- **IAM Role**: a set of permissions assumed by a service (e.g. an EC2 instance
  profile) — no long-lived keys on the box. Grant least privilege.
- For GitHub Actions, prefer **OIDC** federation over storing static AWS keys.

## Cost control / Free Tier tips
- Use one `t3.micro` EC2 instance and stop it when not demoing.
- Set an **AWS Budgets** alert at a low threshold (e.g. $1) to catch surprises.
- ECR storage and data transfer have small costs; delete old image tags.
- Avoid NAT Gateways and idle Load Balancers — they bill per hour even when unused.

## Deploying a container to EC2 (free-tier pattern)
1. Build the image in CI and push to ECR.
2. EC2 instance has an IAM role allowing `ecr:GetAuthorizationToken` + pull.
3. CI triggers an SSM `RunCommand` that makes the instance pull the new image and
   restart the container — no inbound SSH required.
