# Terraform (Infrastructure as Code)

Terraform manages cloud infrastructure declaratively. You describe the desired
state in HCL; Terraform computes and applies the diff to reach it.

## Core workflow
1. `terraform init` — download providers and configure the backend.
2. `terraform plan` — preview the changes (creates/updates/destroys).
3. `terraform apply` — apply the changes.
4. `terraform destroy` — tear everything down.

## Key concepts
- **Provider**: plugin for a platform (aws, google, azurerm).
- **Resource**: a managed infrastructure object (`aws_instance`, `aws_ecr_repository`).
- **Variable / Output**: parameterize inputs and expose results.
- **State**: Terraform's record of real-world resources. Store it remotely (e.g.
  an S3 bucket with DynamoDB locking) so teams share one source of truth.
- **Module**: a reusable, parameterized group of resources.

## State and locking
Never edit state by hand. Use a remote backend so state is shared and locked:
```hcl
terraform {
  backend "s3" {
    bucket         = "my-tf-state"
    key            = "app/terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "tf-locks"
  }
}
```
If a run is interrupted and a lock is stuck, release it with
`terraform force-unlock <LOCK_ID>` (only when you are sure no run is active).

## Good practices
- Pin provider versions with `required_providers`.
- Keep secrets out of `.tf` and state where possible; mark sensitive outputs.
- Run `terraform fmt` and `terraform validate` in CI.
- Use `plan` as a required check before `apply` on protected branches.
- Prefer `for_each` over `count` for stable resource addresses.
