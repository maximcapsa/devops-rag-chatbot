# Copy to terraform.tfvars (gitignored) and fill in. Then: terraform apply
aws_region    = "us-east-1"
project_name  = "devops-rag"
instance_type = "t3.micro"

groq_api_key   = "gsk_your_groq_key"
voyage_api_key = "pa-your_voyage_key"

# Optional: lock the app to your IP, e.g. "203.0.113.4/32"
allow_http_cidr = "0.0.0.0/0"

# Optional: get email alerts for alarms (requires confirming the SNS subscription)
alarm_email = ""
