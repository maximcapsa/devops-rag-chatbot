variable "aws_region" {
  description = "AWS region to deploy into (us-east-1 is the most Free Tier friendly)."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix for all resources."
  type        = string
  default     = "devops-rag"
}

variable "instance_type" {
  description = "EC2 instance type. t3.micro/t2.micro are Free Tier eligible."
  type        = string
  default     = "t3.micro"
}

variable "allow_http_cidr" {
  description = "CIDR allowed to reach the app over HTTP (port 80). Lock this to your IP if you prefer."
  type        = string
  default     = "0.0.0.0/0"
}

variable "groq_api_key" {
  description = "Groq API key (stored as an encrypted SSM SecureString)."
  type        = string
  sensitive   = true
}

variable "voyage_api_key" {
  description = "Voyage AI API key (stored as an encrypted SSM SecureString)."
  type        = string
  sensitive   = true
}

variable "groq_model" {
  type    = string
  default = "llama-3.3-70b-versatile"
}

variable "voyage_model" {
  type    = string
  default = "voyage-3-lite"
}

variable "alarm_email" {
  description = "Optional email for CloudWatch alarm notifications. Leave empty to skip SNS."
  type        = string
  default     = ""
}
